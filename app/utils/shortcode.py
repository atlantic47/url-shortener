"""Short code generation and validation utilities."""

import random
import string
import re
from typing import Optional

# Base62 character set (a-z, A-Z, 0-9)
BASE62_CHARS = string.ascii_letters + string.digits


def generate_short_code(length: int = 7) -> str:
    """
    Generate a random Base62 short code.

    Args:
        length: Length of the short code (default: 7)

    Returns:
        Random alphanumeric string
    """
    return "".join(random.choices(BASE62_CHARS, k=length))


def validate_custom_alias(alias: str) -> tuple[bool, Optional[str]]:
    """
    Validate custom alias format.

    Args:
        alias: Custom alias to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not alias:
        return False, "Custom alias cannot be empty"

    if len(alias) < 3 or len(alias) > 20:
        return False, "Custom alias must be between 3 and 20 characters"

    if not re.match(r"^[a-zA-Z0-9\-]+$", alias):
        return False, "Custom alias must contain only alphanumeric characters and hyphens"

    # Additional checks for reserved words
    reserved_words = ["admin", "api", "health", "analytics", "shorten"]
    if alias.lower() in reserved_words:
        return False, f"Custom alias '{alias}' is reserved"

    return True, None
