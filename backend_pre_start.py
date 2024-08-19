"""
Service pre start checks:
- Check connection to Postres DB, 
- Check connection to test Postres DB,
"""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.config import settings
from src.db.postgres import async_session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 2


async def check_postgres_connection() -> None:
    logging.info("Checking if database %s is available...", settings.POSTGRES_SERVER)
    async with async_session() as session:
        await session.execute(text("SELECT 1;"))
    logging.info("SUCCESS - database is available")


async def check_test_postgres_connection():
    logging.info("Checking if database %s is available...", settings.TEST_POSTGRES_SERVER)
    engine = create_async_engine(settings.TEST_DATABASE_URL.unicode_string())
    async_session = async_sessionmaker(
        engine, autocommit=False, autoflush=False, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        await session.execute(text("SELECT 1;"))
    logging.info("SUCCESS - test database is available")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        await check_postgres_connection()
        await check_test_postgres_connection()
    except Exception as e:
        logger.error("Error initializing service: %s", e)
        raise


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()