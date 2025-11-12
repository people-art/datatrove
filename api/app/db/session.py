"""
Database session management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DB_POOL_SIZE,  # Maximum number of connections in the pool
    max_overflow=settings.DB_MAX_OVERFLOW,  # Maximum overflow connections
    pool_recycle=settings.DB_POOL_RECYCLE,  # Recycle connections after this many seconds
    pool_pre_ping=settings.DB_POOL_PRE_PING,  # Enable connection health checks
    echo=settings.DEBUG,
    future=True,
)

# Create sync engine for Celery tasks
sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DEBUG,
)

# Create async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create sync session factory for Celery tasks
session_factory = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)
