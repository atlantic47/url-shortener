"""Click tracking database model."""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Click(Base):
    """Click model for tracking URL access analytics."""

    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)

    # Timestamp
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(512), nullable=True)
    referer = Column(String(2048), nullable=True)

    # Enriched GeoIP data
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Parsed user agent data
    device_type = Column(String(50), nullable=True)  # mobile, tablet, desktop
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # A/B test variant
    variant = Column(String(1), nullable=True)  # 'A' or 'B'

    # Relationship to URL
    url = relationship("URL", back_populates="clicks")

    def __repr__(self) -> str:
        return f"<Click(url_id={self.url_id}, clicked_at={self.clicked_at})>"
