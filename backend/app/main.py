from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection
from app.api.v1.health import router as health_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.auth.oauth_router import router as oauth_router
from app.api.v1.admin.router import router as admin_router

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
    level="DEBUG" if settings.debug else "INFO",
    colorize=True        # ← ADD THIS
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} 🚀")
    logger.info(f"Environment: {settings.environment}")
    await check_db_connection()
    await check_redis_connection()
    yield
    logger.info("Shutting down SnappCart API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade e-commerce platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1",tags=["Health"])
app.include_router(auth_router, prefix="/api/v1",tags=["Auth"])
app.include_router(oauth_router, prefix="/api/v1",tags=["OAuth"])
app.include_router(admin_router, prefix="/api/v1",tags=["Admin"])