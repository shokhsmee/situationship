"""Inline keyboards for lobby flows."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import settings


def lobby_keyboard(game_id: int, code: str, *, is_host: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    # Telegram rejects non-HTTPS WebApp buttons, so only add it when the Mini App
    # URL is public HTTPS. In local/dev the lobby still works without it.
    if settings.webapp_is_https:
        kb.row(
            InlineKeyboardButton(
                text="🕹 Open Game",
                web_app=WebAppInfo(url=f"{settings.telegram_webapp_url}/lobby/{game_id}"),
            )
        )
    if is_host:
        kb.row(InlineKeyboardButton(text="▶️ Start investigation", callback_data=f"start:{game_id}"))
    kb.row(
        InlineKeyboardButton(
            text="🔗 Invite friends",
            switch_inline_query=f"join_{code}",
        )
    )
    return kb.as_markup()


def scenarios_keyboard(scenarios: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for s in scenarios:
        kb.row(InlineKeyboardButton(text=f"🔎 {s['title']}", callback_data=f"new:{s['id']}"))
    return kb.as_markup()
