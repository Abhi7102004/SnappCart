from fastapi import APIRouter
from loguru import logger
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def check_health():
    db_status = await check_db_connection()
    redis_status = await check_redis_connection()
    health_status = db_status & redis_status
    
    return {
        "status":"healthy" if health_status else "not healthy",
        "version":settings.app_version,
        "environment":settings.environment,
        "services":{
            "api":True,
            "db_status":db_status,
            "redis_status":redis_status
        }
    }
    
@router.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }