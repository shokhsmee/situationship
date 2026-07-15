"""/play — launch the Telegram Mini App (full game UI)."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from bot.config import settings

router = Router()


@router.message(Command("play"))
async def play(message: Message):
    if not settings.webapp_is_https:
        # Telegram Mini App buttons require a public HTTPS URL.
        await message.answer(
            "⚠️ The Mini App needs a public <b>HTTPS</b> URL.\n"
            f"Current <code>TELEGRAM_WEBAPP_URL</code>: {settings.telegram_webapp_url}\n\n"
            "Set it to an HTTPS tunnel (e.g. ngrok/cloudflared) or your deployed domain."
        )
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Open Situationship", web_app=WebAppInfo(url=settings.telegram_webapp_url))]
        ]
    )
    await message.answer("Tap to open the investigation board:", reply_markup=kb)
