"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./url_shortener.db"

    # Application
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 7

    # Rate Limiting
    SHORTEN_RATE_LIMIT: str = "10/minute"
    REDIRECT_RATE_LIMIT: str = "100/minute"

    # GeoIP (optional)
    GEOIP_DB_PATH: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env file
    )


# Global settings instance
settings = Settings()
