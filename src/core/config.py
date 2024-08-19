import logging
import typing as tp
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


class SystemLanguage(str, Enum):
    """Possible system languages."""
    en = 'en'
    ru = 'ru'


class Settings(BaseSettings):
    """
    Contains env variables and other app's settings. 
    env searching order: 
    - os environ, 
    - .env file, 
    - default values setted here
    """
    model_config = SettingsConfigDict(env_file=f'{PROJECT_DIR}/.env',
                                      env_file_encoding='utf-8',
                                      case_sensitive=True,
                                      extra='ignore')

    SESSION_SECRET_KEY: str  # openssl rand -hex 32

    SYSTEM_LANGUAGE: SystemLanguage = SystemLanguage.en

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: tp.Optional[PostgresDsn] = None

    TEST_POSTGRES_SERVER: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASSWORD: str
    TEST_POSTGRES_DB: str
    TEST_DATABASE_URL: PostgresDsn

    DEBUG: bool = False

    API_REQUEST_LIMIT_PER_MINUTE: int

    @model_validator(mode='before')
    @classmethod
    def assemble_db_urls(cls, values: dict[str, tp.Any]):
        # Add debug logging for the values
        logging.debug("Assembling DATABASE_URL with values: %s", values)

        if not all([values.get("POSTGRES_USER"), values.get("POSTGRES_PASSWORD"),
                    values.get("POSTGRES_SERVER"), values.get("POSTGRES_DB")]):
            raise ValueError("Missing required PostgreSQL environment variables.")

        values["DATABASE_URL"] = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB')}"  # Ensure the path starts with a forward slash
        )
        values["TEST_DATABASE_URL"] = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("TEST_POSTGRES_USER"),
            password=values.get("TEST_POSTGRES_PASSWORD"),
            host=values.get("TEST_POSTGRES_SERVER"),
            path=values.get("TEST_POSTGRES_DB")
        )
        logging.debug("Constructed DATABASE_URL: %s", values["DATABASE_URL"])
        return values


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

logging_level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
)

# Log the final settings to verify correct loading
logging.debug("Final settings: %s", settings.dict())
