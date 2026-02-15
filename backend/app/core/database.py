"""
Database connection and session management.
Uses SQLAlchemy with PostgreSQL.
"""
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight compatibility migration for RBAC ownership.
        await conn.execute(
            text(
                "ALTER TABLE documents "
                "ADD COLUMN IF NOT EXISTS owner_id VARCHAR(128)"
            )
        )
        await conn.execute(
            text(
                "UPDATE documents "
                "SET owner_id = 'legacy-owner' "
                "WHERE owner_id IS NULL"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_documents_owner_id "
                "ON documents (owner_id)"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE documents "
                "ALTER COLUMN owner_id SET NOT NULL"
            )
        )


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
