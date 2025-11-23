"""Pydantic schemas package."""

from app.schemas.url import (
    ABTestConfig,
    ShortenRequest,
    ShortenResponse,
    URLResponse
)
from app.schemas.analytics import (
    ClicksByDay,
    TopCountry,
    TopCity,
    DeviceBreakdown,
    BrowserBreakdown,
    OSBreakdown,
    ABTestResults,
    AnalyticsResponse
)

__all__ = [
    "ABTestConfig",
    "ShortenRequest",
    "ShortenResponse",
    "URLResponse",
    "ClicksByDay",
    "TopCountry",
    "TopCity",
    "DeviceBreakdown",
    "BrowserBreakdown",
    "OSBreakdown",
    "ABTestResults",
    "AnalyticsResponse"
]
