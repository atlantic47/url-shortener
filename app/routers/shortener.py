"""URL shortening router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.url_service import create_short_url
from app.utils.rate_limiter import limiter
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["shortener"])


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
@limiter.limit(settings.SHORTEN_RATE_LIMIT)
async def shorten_url(
    request: Request,
    shorten_request: ShortenRequest,
    db: AsyncSession = Depends(get_db)
) -> ShortenResponse:
    """
    Create a shortened URL.

    **Rate Limit:** 10 requests per minute per IP

    **Request Body:**
    - original_url: The URL to shorten (required)
    - ttl_seconds: Time-to-live in seconds (optional)
    - custom_alias: Custom short code (optional, 3-20 alphanumeric chars + hyphens)
    - ab_test: A/B test configuration with url_b and split percentage (optional)

    **Returns:**
    - short_url: Full shortened URL
    - short_code: The short code
    - expires_at: Expiry timestamp (if TTL was set)
    - created_at: Creation timestamp
    """
    try:
        url = await create_short_url(db, shorten_request)

        # Build short URL
        short_url = f"{settings.BASE_URL}/{url.short_code}"

        return ShortenResponse(
            short_url=short_url,
            short_code=url.short_code,
            expires_at=url.expires_at,
            created_at=url.created_at
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
