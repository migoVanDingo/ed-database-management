# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://..."
    REDIS_URL: str = "redis://redis:6379/0"
    DEBUG_PUBSUB_PRINT: bool = False  # flip to True for the test


settings = Settings()
