"""Analytics router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import get_analytics

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])


@router.get("/analytics/{short_code}", response_model=AnalyticsResponse)
async def get_url_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_db)
) -> AnalyticsResponse:
    """
    Get analytics for a shortened URL.

    **Path Parameters:**
    - short_code: The short code to get analytics for

    **Returns:**
    - Aggregated analytics including:
      - Total clicks and unique visitors
      - First and last click timestamps
      - Clicks by day
      - Geographic breakdown (countries and cities)
      - Device, browser, and OS statistics
      - A/B test results (if applicable)
    """
    analytics = await get_analytics(db, short_code)

    if not analytics:
        logger.warning(f"Analytics requested for non-existent short code: {short_code}")
        raise HTTPException(status_code=404, detail="Short URL not found")

    logger.info(f"Analytics retrieved for {short_code}: {analytics.total_clicks} clicks")
    return analytics
