"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address


def get_limiter() -> Limiter:
    """
    Create and configure rate limiter.

    Uses in-memory storage for demo purposes.
    For production, use Redis backend.
    """
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri="memory://",
        strategy="fixed-window"
    )
    return limiter


# Global limiter instance
limiter = get_limiter()
