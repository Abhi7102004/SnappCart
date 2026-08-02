import re
from typing import Optional


def validate_password_strength(v: str) -> str:
    """
    8-128 chars, at least one uppercase, one lowercase, one number.
    """
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v) > 128:
        raise ValueError("Password must be at most 128 characters")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", v):
        raise ValueError("Password must contain at least one number")
    return v


def validate_phone_e164(v: Optional[str]) -> Optional[str]:
    """
    E.164 format: +[country code][number].
    """
    if v is None:
        return v
    if not re.match(r"^\+[1-9]\d{6,14}$", v):
        raise ValueError("Phone must be in E.164 format (+919838388338)")
    return v


def validate_full_name(v: Optional[str]) -> Optional[str]:
    """
    2-100 chars, stripped.
    """
    if v is None:
        return v
    v = v.strip()
    if len(v) < 2:
        raise ValueError("Full name must be at least 2 characters")
    if len(v) > 100:
        raise ValueError("Full name must be at most 100 characters")
    return v