"""Analytics tracking and retrieval service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from datetime import datetime
from typing import Optional
import logging

from app.models import Click, URL
from app.services.enrichment import enrich_ip_address, parse_user_agent
from app.schemas.analytics import (
    AnalyticsResponse,
    ClicksByDay,
    TopCountry,
    TopCity,
    DeviceBreakdown,
    BrowserBreakdown,
    OSBreakdown,
    ABTestResults
)

logger = logging.getLogger(__name__)


async def capture_click(
    db: AsyncSession,
    url_id: int,
    ip_address: Optional[str],
    user_agent: Optional[str],
    referer: Optional[str],
    variant: str
) -> None:
    """
    Capture click analytics with enrichment.

    Args:
        db: Database session
        url_id: URL ID
        ip_address: Client IP address
        user_agent: User agent string
        referer: HTTP referer
        variant: A/B test variant ('A' or 'B')
    """
    # Enrich IP address
    country, city = enrich_ip_address(ip_address)

    # Parse user agent
    device_type, browser, os = parse_user_agent(user_agent)

    # Create click record
    click = Click(
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        country=country,
        city=city,
        device_type=device_type,
        browser=browser,
        os=os,
        variant=variant
    )

    db.add(click)
    await db.commit()
    logger.debug(f"Captured click for URL ID {url_id}")


async def get_analytics(
    db: AsyncSession,
    short_code: str
) -> Optional[AnalyticsResponse]:
    """
    Get aggregated analytics for a short URL.

    Args:
        db: Database session
        short_code: Short code to get analytics for

    Returns:
        AnalyticsResponse if URL exists, None otherwise
    """
    # Get URL
    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()

    if not url:
        return None

    # Total clicks
    stmt = select(func.count(Click.id)).where(Click.url_id == url.id)
    result = await db.execute(stmt)
    total_clicks = result.scalar() or 0

    # Unique visitors (by IP)
    stmt = select(func.count(distinct(Click.ip_address))).where(Click.url_id == url.id)
    result = await db.execute(stmt)
    unique_visitors = result.scalar() or 0

    # First and last click
    stmt = select(func.min(Click.clicked_at)).where(Click.url_id == url.id)
    result = await db.execute(stmt)
    first_click = result.scalar()

    stmt = select(func.max(Click.clicked_at)).where(Click.url_id == url.id)
    result = await db.execute(stmt)
    last_click = result.scalar()

    # Clicks by day
    stmt = (
        select(
            func.date(Click.clicked_at).label("date"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .group_by(func.date(Click.clicked_at))
        .order_by(func.date(Click.clicked_at))
    )
    result = await db.execute(stmt)
    clicks_by_day = [
        ClicksByDay(date=row.date, count=row.count)
        for row in result.all()
    ]

    # Top countries
    stmt = (
        select(
            Click.country.label("country"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .where(Click.country.isnot(None))
        .group_by(Click.country)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    top_countries = [
        TopCountry(country=row.country, count=row.count)
        for row in result.all()
    ]

    # Top cities
    stmt = (
        select(
            Click.city.label("city"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .where(Click.city.isnot(None))
        .group_by(Click.city)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    top_cities = [
        TopCity(city=row.city, count=row.count)
        for row in result.all()
    ]

    # Device breakdown
    stmt = (
        select(
            Click.device_type.label("device"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .where(Click.device_type.isnot(None))
        .group_by(Click.device_type)
        .order_by(func.count(Click.id).desc())
    )
    result = await db.execute(stmt)
    devices = [
        DeviceBreakdown(device=row.device, count=row.count)
        for row in result.all()
    ]

    # Browser breakdown
    stmt = (
        select(
            Click.browser.label("browser"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .where(Click.browser.isnot(None))
        .group_by(Click.browser)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    browsers = [
        BrowserBreakdown(browser=row.browser, count=row.count)
        for row in result.all()
    ]

    # OS breakdown
    stmt = (
        select(
            Click.os.label("os"),
            func.count(Click.id).label("count")
        )
        .where(Click.url_id == url.id)
        .where(Click.os.isnot(None))
        .group_by(Click.os)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    operating_systems = [
        OSBreakdown(os=row.os, count=row.count)
        for row in result.all()
    ]

    # A/B test results
    ab_test_results = None
    if url.url_b:
        stmt = select(func.count(Click.id)).where(Click.url_id == url.id).where(Click.variant == "A")
        result = await db.execute(stmt)
        variant_a_clicks = result.scalar() or 0

        stmt = select(func.count(Click.id)).where(Click.url_id == url.id).where(Click.variant == "B")
        result = await db.execute(stmt)
        variant_b_clicks = result.scalar() or 0

        ab_test_results = ABTestResults(
            variant_a_clicks=variant_a_clicks,
            variant_b_clicks=variant_b_clicks
        )

    return AnalyticsResponse(
        short_code=short_code,
        total_clicks=total_clicks,
        unique_visitors=unique_visitors,
        first_click=first_click,
        last_click=last_click,
        clicks_by_day=clicks_by_day,
        top_countries=top_countries,
        top_cities=top_cities,
        devices=devices,
        browsers=browsers,
        operating_systems=operating_systems,
        ab_test_results=ab_test_results
    )
