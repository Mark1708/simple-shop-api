"""Dependency injections for getting DB connections."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import async_session


async def get_db() -> AsyncSession:
    """Returns DB storage connection."""
    async with async_session() as session:
        yield session