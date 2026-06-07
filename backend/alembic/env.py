# backend/alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# ── Add backend/ to Python path ──────────────────────────
# Without this, "from app.core.config import settings"
# would fail with ModuleNotFoundError
# os.path.dirname(__file__) = alembic/ folder
# os.path.dirname(that)     = backend/ folder
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Import our app's settings and Base ───────────────────
from app.core.config import settings
from app.core.database import Base

# ── Import ALL models ─────────────────────────────────────
# CRITICAL: every model must be imported here
# Alembic detects tables through Base.metadata
# If model not imported → Alembic can't see it
# → won't generate migration for it
from app.models import user  # noqa: F401
# noqa: F401 = tells linter "yes I know I'm not
# 'using' this import, it's intentional"

# ── Alembic config object ─────────────────────────────────
config = context.config

# ── Override database URL with our .env value ─────────────
# This replaces whatever is in alembic.ini
# Now alembic reads DATABASE_URL from .env ✅
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url
)

# ── Setup logging ─────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Target metadata ───────────────────────────────────────
# This is what Alembic compares against the DB
# Base.metadata knows about ALL imported models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations without DB connection.
    Used for generating SQL scripts.
    Rarely used in practice.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations with live DB connection.
    This is what we always use.
    NullPool = no connection pooling for migrations
    (migrations run once and exit, no need for pool)
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# ── Run the appropriate mode ──────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()