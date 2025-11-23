"""URL management service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.models import URL
from app.schemas.url import ShortenRequest
from app.utils.shortcode import generate_short_code, validate_custom_alias
from app.config import settings

logger = logging.getLogger(__name__)


async def create_short_url(
    db: AsyncSession,
    request: ShortenRequest
) -> URL:
    """
    Create a new shortened URL.

    Args:
        db: Database session
        request: URL shortening request

    Returns:
        Created URL object

    Raises:
        ValueError: If custom alias is invalid or already taken
        RuntimeError: If unable to generate unique short code after max attempts
    """
    # Validate custom alias if provided
    if request.custom_alias:
        is_valid, error_msg = validate_custom_alias(request.custom_alias)
        if not is_valid:
            raise ValueError(error_msg)

        # Check if custom alias already exists
        stmt = select(URL).where(URL.short_code == request.custom_alias)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Custom alias '{request.custom_alias}' is already taken")

        short_code = request.custom_alias
    else:
        # Generate unique short code with collision retry
        max_attempts = 3
        short_code = None

        for attempt in range(max_attempts):
            candidate = generate_short_code(settings.SHORT_CODE_LENGTH)

            # Check for collision
            stmt = select(URL).where(URL.short_code == candidate)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                short_code = candidate
                break

            logger.warning(f"Short code collision on attempt {attempt + 1}: {candidate}")

        if not short_code:
            raise RuntimeError("Unable to generate unique short code after maximum attempts")

    # Calculate expiry time
    expires_at = None
    if request.ttl_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=request.ttl_seconds)

    # Prepare A/B test data
    url_b = None
    ab_split = None
    if request.ab_test:
        url_b = str(request.ab_test.url_b)
        ab_split = float(request.ab_test.split)

    # Create URL record
    url = URL(
        short_code=short_code,
        original_url=str(request.original_url),
        url_b=url_b,
        ab_split=ab_split,
        custom_alias=request.custom_alias,
        expires_at=expires_at,
        is_active=True
    )

    db.add(url)

    try:
        await db.commit()
        await db.refresh(url)
        logger.info(f"Created short URL: {short_code}")
        return url
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Database integrity error: {e}")
        raise ValueError("Failed to create short URL due to duplicate constraint")


async def get_url_by_code(
    db: AsyncSession,
    short_code: str
) -> Optional[URL]:
    """
    Get URL by short code with expiry checking.

    Args:
        db: Database session
        short_code: Short code to look up

    Returns:
        URL object if found and not expired, None otherwise
    """
    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()

    if not url:
        return None

    # Check if URL is active
    if not url.is_active:
        return None

    # Check if URL has expired (lazy deletion)
    if url.expires_at and url.expires_at < datetime.utcnow():
        logger.info(f"URL {short_code} has expired")
        return None

    return url


async def get_url_by_id(
    db: AsyncSession,
    url_id: int
) -> Optional[URL]:
    """
    Get URL by ID.

    Args:
        db: Database session
        url_id: URL ID

    Returns:
        URL object if found, None otherwise
    """
    stmt = select(URL).where(URL.id == url_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
