"""Database session factory"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.models import Base


async def init_db(database_url: str) -> None:
    """Initialize database"""
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session_factory(database_url: str) -> async_sessionmaker:
    """Get session factory"""
    engine = create_async_engine(database_url, echo=False)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
