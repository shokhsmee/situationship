"""Application configuration via pydantic-settings.

Single source of truth for all runtime configuration. Nothing else should read
os.environ directly.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "Situationship"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://situationship:situationship@localhost:5432/situationship",
        description="Async SQLAlchemy DSN (asyncpg driver).",
    )

    # --- Redis ---
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- Security / JWT ---
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # --- Telegram ---
    telegram_bot_token: str = Field(default="")
    telegram_webapp_url: str = Field(default="http://localhost:5173")

    # --- CORS ---
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # --- Gameplay defaults (seconds) ---
    default_intro_seconds: int = 60
    default_evidence_seconds: int = 90
    default_discussion_seconds: int = 120
    default_vote_seconds: int = 60
    default_rounds: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
