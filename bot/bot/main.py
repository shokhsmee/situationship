"""Bot entrypoint: wire middleware + routers, run long-polling."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.handlers import game, lobby, start, webapp
from bot.middlewares.auth_mw import AuthMiddleware
from bot.services.api_client import api


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    auth = AuthMiddleware()
    dp.message.middleware(auth)
    dp.callback_query.middleware(auth)
    dp.include_router(start.router)
    dp.include_router(lobby.router)
    dp.include_router(game.router)
    dp.include_router(webapp.router)
    return dp


async def main() -> None:
    if not settings.telegram_bot_token:
        # Cleanly disabled (exit 0) so `restart: on-failure` won't loop it.
        logging.warning("TELEGRAM_BOT_TOKEN is not set — bot disabled.")
        return
    bot = Bot(
        settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()
    try:
        await dp.start_polling(bot)
    finally:
        await api.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
