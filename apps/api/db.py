"""SQLite session factory and table initialisation."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings
from models import Base

_engine = None
_session_factory = None


def _get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.api_debug,
            connect_args={"check_same_thread": False},
        )
    return _engine


def _get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def init_db():
    """Create all tables if they don't exist."""
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """FastAPI dependency that yields a database session."""
    factory = _get_session_factory()
    async with factory() as session:
        yield session


def reset_engine():
    """Reset the database engine (use in tests only)."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None
