import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"
_ENV_VALUES = dotenv_values(_ENV_FILE, encoding="utf-8-sig")

_DATABASE_URL = (
    os.environ.get("DATABASE_URL")
    or _ENV_VALUES.get("DATABASE_URL")
    or "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/vigil"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "VIGIL"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = _DATABASE_URL
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    nvd_api_key: Optional[str] = None
    osv_api_url: str = "https://api.osv.dev/v1"

    # Development-only escape hatch. When enabled, endpoints that have no
    # database-backed implementation may return clearly-labelled simulated demo
    # fixtures. It defaults to False so VIGIL never presents simulated records as
    # real security findings, and it is NEVER used to mask a database error — a
    # failed query always surfaces as an error response.
    enable_demo_mode: bool = False

    @property
    def APP_NAME(self) -> str:
        return self.app_name

    @property
    def APP_VERSION(self) -> str:
        return self.app_version

    @property
    def DEBUG(self) -> bool:
        return self.debug

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def REDIS_URL(self) -> str:
        return self.redis_url

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.access_token_expire_minutes

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return self.cors_origins

    @property
    def NVD_API_KEY(self) -> Optional[str]:
        return self.nvd_api_key

    @property
    def OSV_API_URL(self) -> str:
        return self.osv_api_url

    @property
    def ENABLE_DEMO_MODE(self) -> bool:
        return self.enable_demo_mode


settings = Settings()
