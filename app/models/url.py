"""URL database model."""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class URL(Base):
    """URL model for storing shortened URLs."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    short_code = Column(String(20), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), nullable=False)

    # A/B Testing fields
    url_b = Column(String(2048), nullable=True)
    ab_split = Column(Float, nullable=True)  # Percentage for variant A (0-100)

    # Custom alias
    custom_alias = Column(String(20), nullable=True)

    # Timestamps and expiry
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship to clicks
    clicks = relationship("Click", back_populates="url", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<URL(short_code={self.short_code}, original_url={self.original_url})>"
