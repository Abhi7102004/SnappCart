
from pydantic_settings import BaseSettings
from functools import lru_cache
from loguru import logger


class Settings(BaseSettings):
    # App
    app_name: str = "SnappCart API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Redis
    redis_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    frontend_url: str = "http://localhost:3000"
    
    #OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    ses_from_email: str = ""
    ses_from_name: str = "SnappCart"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Cache settings so .env is only read once.
    lru_cache = same object returned every time.
    """
    settings = Settings()
    logger.info(f"Settings loaded for environment: {settings.environment}")
    return settings


settings = get_settings()