from datetime import date
from decimal import Decimal
import re


def json_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def validate_name(text: str) -> bool:
    """Validates customer names - letters, spaces, hyphens, apostrophes only."""
    if not text or len(text) > 100:
        return False
    return bool(re.match(r"^[a-zA-Z\s\-']+$", text))


def validate_product_search(text: str) -> bool:
    """Validates product search terms - blocks dangerous characters."""
    if not text or len(text) > 100:
        return False
    dangerous = re.compile(r"[;\"\\\x00-\x1f]")
    return not dangerous.search(text)


def validate_id(text: str) -> bool:
    """Order IDs should be numeric only."""
    return bool(text and text.isdigit())
