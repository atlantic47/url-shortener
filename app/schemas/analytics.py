"""Pydantic schemas for analytics."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ClicksByDay(BaseModel):
    """Daily click count."""

    date: date
    count: int


class TopCountry(BaseModel):
    """Country click statistics."""

    country: str
    count: int


class TopCity(BaseModel):
    """City click statistics."""

    city: str
    count: int


class DeviceBreakdown(BaseModel):
    """Device type statistics."""

    device: str
    count: int


class BrowserBreakdown(BaseModel):
    """Browser statistics."""

    browser: str
    count: int


class OSBreakdown(BaseModel):
    """Operating system statistics."""

    os: str
    count: int


class ABTestResults(BaseModel):
    """A/B test results."""

    variant_a_clicks: int
    variant_b_clicks: int


class AnalyticsResponse(BaseModel):
    """Complete analytics response."""

    short_code: str
    total_clicks: int
    unique_visitors: int
    first_click: Optional[datetime]
    last_click: Optional[datetime]
    clicks_by_day: list[ClicksByDay]
    top_countries: list[TopCountry]
    top_cities: list[TopCity]
    devices: list[DeviceBreakdown]
    browsers: list[BrowserBreakdown]
    operating_systems: list[OSBreakdown]
    ab_test_results: Optional[ABTestResults]

    model_config = {"from_attributes": True}
