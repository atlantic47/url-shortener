"""URL redirection router."""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import random
import logging

from app.database import get_db
from app.services.url_service import get_url_by_code
from app.services.analytics_service import capture_click
from app.utils.rate_limiter import limiter
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["redirect"])


def select_ab_variant(ab_split: float) -> str:
    """
    Select A/B test variant based on split percentage.

    Args:
        ab_split: Percentage for variant A (0-100)

    Returns:
        'A' or 'B'
    """
    return "A" if random.random() * 100 < ab_split else "B"


@router.get("/{short_code}")
@limiter.limit(settings.REDIRECT_RATE_LIMIT)
async def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Redirect to the original URL.

    **Rate Limit:** 100 requests per minute per IP

    **Path Parameters:**
    - short_code: The short code to redirect

    **Returns:**
    - HTTP 307 redirect to the original URL
    - HTTP 404 if short code not found
    - HTTP 410 if URL has expired
    """
    url = await get_url_by_code(db, short_code)

    if not url:
        logger.info(f"Short code not found or expired: {short_code}")
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Check expiry (returns None if expired in get_url_by_code)
    # If we got here, URL is valid but let's double-check expiry for 410 response
    from datetime import datetime
    if url.expires_at and url.expires_at < datetime.utcnow():
        logger.info(f"URL expired: {short_code}")
        raise HTTPException(status_code=410, detail="Short URL has expired")

    # Determine target URL based on A/B test
    variant = "A"
    target_url = url.original_url

    if url.url_b and url.ab_split is not None:
        variant = select_ab_variant(url.ab_split)
        if variant == "B":
            target_url = url.url_b
        logger.debug(f"A/B test: selected variant {variant} for {short_code}")

    # Extract request metadata
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")

    # Capture analytics in background (non-blocking)
    background_tasks.add_task(
        capture_click,
        db=db,
        url_id=url.id,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        variant=variant
    )

    logger.info(f"Redirecting {short_code} to {target_url}")
    return RedirectResponse(url=target_url, status_code=307)
