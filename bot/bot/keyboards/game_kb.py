"""Inline keyboards for in-game flows."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import settings


def open_game_keyboard(game_id: int) -> InlineKeyboardMarkup | None:
    # Only offer the Mini App button over public HTTPS (Telegram requirement).
    if not settings.webapp_is_https:
        return None
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="🎭 Open the investigation",
            web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/game/{game_id}"),
        )
    )
    return kb.as_markup()
