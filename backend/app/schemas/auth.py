from pydantic import BaseModel

from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str
    language: str = "en"


class LoginRequest(BaseModel):
    username: str
    password: str


class TelegramAuthRequest(BaseModel):
    """Raw `initData` string from the Telegram WebApp SDK."""

    init_data: str


class BotAuthRequest(BaseModel):
    """Server-to-server auth from the Telegram bot (trusted via the bot token)."""

    bot_token: str
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    language_code: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
