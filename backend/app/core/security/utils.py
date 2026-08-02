from datetime import datetime, timezone

def ensure_utc(dt: datetime | None) -> datetime | None:
    """
    Make a datetime timezone-aware (UTC) if it isn't already.
    PostgreSQL sometimes returns naive datetimes depending on
    column config — always compare against aware `now()` safely.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_expired(expires_at: datetime | None) -> bool:
    """True if given expiry datetime is in the past (or None = no expiry set = not expired)"""
    if expires_at is None:
        return False
    return ensure_utc(expires_at) < datetime.now(timezone.utc)


def utc_now() -> datetime:
    """Shorthand for current UTC time — used everywhere instead of repeating this"""
    return datetime.now(timezone.utc)