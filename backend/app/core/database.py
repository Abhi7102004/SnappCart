from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from loguru import logger
from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass

def get_db():
    """
    Yields a DB session and ensures it's
    always closed even if an error occurs.
    Used as FastAPI dependency.
    """
    db=SessionLocal()
    
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        
async def check_db_connection()->bool:
    """
    Health check — verify DB is reachable.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("Select 1"))
        logger.info("PostgreSQL connection: OK ✅")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False
    
    