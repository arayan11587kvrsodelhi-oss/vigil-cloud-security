from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "VIGIL"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vigil"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Security intelligence API keys (optional, use free tiers by default)
    NVD_API_KEY: Optional[str] = None
    OSV_API_URL: str = "https://api.osv.dev/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()