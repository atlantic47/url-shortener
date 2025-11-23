"""Pydantic schemas for URL operations."""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class ABTestConfig(BaseModel):
    """Configuration for A/B testing."""

    url_b: HttpUrl
    split: int = Field(ge=0, le=100, description="Percentage of traffic for variant A (0-100)")


class ShortenRequest(BaseModel):
    """Request schema for creating a shortened URL."""

    original_url: HttpUrl
    ttl_seconds: Optional[int] = Field(None, ge=1, description="Time-to-live in seconds")
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=20)
    ab_test: Optional[ABTestConfig] = None

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: Optional[str]) -> Optional[str]:
        """Validate custom alias format."""
        if v is not None:
            if not re.match(r"^[a-zA-Z0-9\-]+$", v):
                raise ValueError("Custom alias must contain only alphanumeric characters and hyphens")
        return v


class ShortenResponse(BaseModel):
    """Response schema for shortened URL creation."""

    short_url: str
    short_code: str
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class URLResponse(BaseModel):
    """Detailed URL information response."""

    id: int
    short_code: str
    original_url: str
    url_b: Optional[str]
    ab_split: Optional[float]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    model_config = {"from_attributes": True}
