# app/core/security/jwt.py

from datetime import timedelta
from jose import jwt
from app.core.config import settings
from app.core.constants import REFRESH_TOKEN_PREFIX
from app.core.security.utils import utc_now


def get_refresh_token_key(user_id: str) -> str:
    return f"{REFRESH_TOKEN_PREFIX}{user_id}"


def create_access_token(user_id: str, role: str) -> str:
    expire = utc_now() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": utc_now(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: str) -> str:
    expire = utc_now() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": utc_now(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """Decode and verify JWT. Raises JWTError if invalid/expired."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])