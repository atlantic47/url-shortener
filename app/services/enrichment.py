"""Data enrichment services for GeoIP and User-Agent parsing."""

from typing import Optional, Tuple
import logging
from user_agents import parse as parse_ua

logger = logging.getLogger(__name__)

# GeoIP functionality (optional)
try:
    import geoip2.database
    from app.config import settings

    GEOIP_AVAILABLE = settings.GEOIP_DB_PATH is not None
    if GEOIP_AVAILABLE:
        try:
            geoip_reader = geoip2.database.Reader(settings.GEOIP_DB_PATH)
        except Exception as e:
            logger.warning(f"GeoIP database not available: {e}")
            GEOIP_AVAILABLE = False
            geoip_reader = None
    else:
        geoip_reader = None
except ImportError:
    logger.warning("geoip2 library not installed")
    GEOIP_AVAILABLE = False
    geoip_reader = None


def enrich_ip_address(ip_address: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Enrich IP address with GeoIP data.

    Args:
        ip_address: IP address to enrich

    Returns:
        Tuple of (country, city)
    """
    if not ip_address or not GEOIP_AVAILABLE or not geoip_reader:
        return None, None

    try:
        response = geoip_reader.city(ip_address)
        country = response.country.name if response.country.name else None
        city = response.city.name if response.city.name else None
        return country, city
    except Exception as e:
        logger.debug(f"GeoIP lookup failed for {ip_address}: {e}")
        return None, None


def parse_user_agent(user_agent_string: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse user agent string to extract device, browser, and OS.

    Args:
        user_agent_string: User agent string to parse

    Returns:
        Tuple of (device_type, browser, os)
    """
    if not user_agent_string:
        return None, None, None

    try:
        user_agent = parse_ua(user_agent_string)

        # Determine device type
        if user_agent.is_mobile:
            device_type = "mobile"
        elif user_agent.is_tablet:
            device_type = "tablet"
        elif user_agent.is_pc:
            device_type = "desktop"
        else:
            device_type = "other"

        # Extract browser
        browser = user_agent.browser.family if user_agent.browser.family else None

        # Extract OS
        os = user_agent.os.family if user_agent.os.family else None

        return device_type, browser, os
    except Exception as e:
        logger.debug(f"User agent parsing failed: {e}")
        return None, None, None
