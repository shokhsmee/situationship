"""Bot configuration via pydantic-settings."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    telegram_bot_token: str = Field(default="")
    # Backend API root (compose service name in production).
    api_base_url: str = Field(default="http://localhost:8000/api/v1")
    # Public Mini App URL launched via the WebApp button.
    telegram_webapp_url: str = Field(default="http://localhost:5173")

    @property
    def webapp_is_https(self) -> bool:
        """Telegram only accepts WebApp (Mini App) buttons over public HTTPS."""
        return self.telegram_webapp_url.lower().startswith("https://")


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()


settings = get_settings()
