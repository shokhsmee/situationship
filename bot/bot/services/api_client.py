"""Thin async client over the FastAPI backend.

The bot authenticates each Telegram user server-to-server via `/auth/bot`
(trusted by the shared bot token) and caches the resulting JWT in memory.
"""
from __future__ import annotations

import httpx

from bot.config import settings


class ApiClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=settings.api_base_url, timeout=15)
        self._tokens: dict[int, str] = {}  # telegram_id -> JWT
        # Bot-side room membership so we can DM roles on start: game_id -> tg_ids.
        self._members: dict[int, set[int]] = {}

    async def close(self) -> None:
        await self._client.aclose()

    def track_member(self, game_id: int, telegram_id: int) -> None:
        self._members.setdefault(game_id, set()).add(telegram_id)

    def members(self, game_id: int) -> set[int]:
        return self._members.get(game_id, set())

    def _headers(self, telegram_id: int) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._tokens[telegram_id]}"}

    async def authenticate(self, tg_user) -> str:
        """Get-or-create the backend user for a Telegram user; cache the JWT."""
        resp = await self._client.post(
            "/auth/bot",
            json={
                "bot_token": settings.telegram_bot_token,
                "telegram_id": tg_user.id,
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "language_code": tg_user.language_code or "en",
            },
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        self._tokens[tg_user.id] = token
        return token

    def has_token(self, telegram_id: int) -> bool:
        return telegram_id in self._tokens

    # -- Games --------------------------------------------------------------
    async def list_scenarios(self) -> list[dict]:
        return (await self._client.get("/games/scenarios")).json()

    async def create_game(self, telegram_id: int, scenario_id: int) -> dict:
        resp = await self._client.post(
            "/games", json={"scenario_id": scenario_id}, headers=self._headers(telegram_id)
        )
        resp.raise_for_status()
        return resp.json()

    async def join_game(self, telegram_id: int, code: str) -> dict:
        resp = await self._client.post(
            "/games/join", json={"code": code}, headers=self._headers(telegram_id)
        )
        resp.raise_for_status()
        return resp.json()

    async def start_game(self, telegram_id: int, game_id: int) -> dict:
        resp = await self._client.post(
            f"/games/{game_id}/start", headers=self._headers(telegram_id)
        )
        resp.raise_for_status()
        return resp.json()

    async def get_state(self, telegram_id: int, game_id: int) -> dict:
        resp = await self._client.get(
            f"/games/{game_id}/state", headers=self._headers(telegram_id)
        )
        resp.raise_for_status()
        return resp.json()


api = ApiClient()
