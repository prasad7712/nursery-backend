"""SQLAlchemy database configuration with async support and FastAPI dependency injection"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import text
from fastapi import Depends
import os


# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/nursery_db"
)

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection function for FastAPI endpoints.
    
    Usage:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - creates all tables.
    
    Call this on application startup to create schema.
    """
    from src.models.base import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    """Dispose of database engine - closes all connections.
    
    Call this on application shutdown.
    """
    await engine.dispose()


async def health_check() -> bool:
    """Check database connection health.
    
    Returns:
        True if database is reachable, False otherwise
    """
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False
