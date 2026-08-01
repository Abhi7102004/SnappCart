from datetime import datetime, timedelta, timezone
from jose import JWTError,jwt
from app.core.config import settings

def create_access_token(user_id:str,role:str) ->str:
    """Create short-lived access token (30 mins)"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)

def create_refresh_token(user_id:str) ->str:
    """Create long-lived refresh token (7 days)"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm)
    
    
def decode_token(token:str) ->dict:
    """
    Decode and verify JWT.
    Raises JWTError if invalid/expired.
    """
    try:
        payload = jwt.decode(token,settings.secret_key,algorithm=settings.algorithm)
        return payload
    except JWTError as e:
        raise JWTError(str(e))
        