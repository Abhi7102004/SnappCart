import redis.asyncio as aioredis
from loguru import logger
from app.core.config import settings

redis_client = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)

async def check_redis_connection() -> bool:
    try:
        await redis_client.ping()
        logger.info("Redis connection: OK ✅")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False
   
    
async def get_redis():
    return redis_client
