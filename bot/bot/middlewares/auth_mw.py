"""Middleware that ensures the Telegram user has a backend JWT before handling.

Injects the shared `ApiClient` into handler data as `api`.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.services.api_client import api


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user and not user.is_bot and not api.has_token(user.id):
            try:
                await api.authenticate(user)
            except Exception:
                # Backend unreachable / auth failure — let the handler decide.
                pass
        data["api"] = api
        return await handler(event, data)
