"""Per-room WebSocket connection manager with a Redis pub/sub bridge.

The engine publishes room events to Redis (so they cross worker processes). Each
worker holding a live connection for a game subscribes once and fans events out
to its local sockets. Broadcast payloads are non-secret by construction; private
per-player state is delivered separately via `send_personal`.
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket

from app.core.redis import subscribe_room


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = {}
        self._meta: dict[WebSocket, dict[str, Any]] = {}
        self._bridges: dict[int, asyncio.Task] = {}

    async def connect(
        self, game_id: int, ws: WebSocket, *, user_id: int, player_id: int
    ) -> None:
        await ws.accept()
        self._rooms.setdefault(game_id, set()).add(ws)
        self._meta[ws] = {"user_id": user_id, "player_id": player_id, "game_id": game_id}
        if game_id not in self._bridges:
            self._bridges[game_id] = asyncio.create_task(self._bridge(game_id))

    def disconnect(self, ws: WebSocket) -> int | None:
        meta = self._meta.pop(ws, None)
        if meta is None:
            return None
        game_id = meta["game_id"]
        room = self._rooms.get(game_id)
        if room:
            room.discard(ws)
            if not room:
                self._rooms.pop(game_id, None)
                bridge = self._bridges.pop(game_id, None)
                if bridge and not bridge.done():
                    bridge.cancel()
        return meta.get("player_id")

    def players_online(self, game_id: int) -> set[int]:
        return {
            self._meta[ws]["player_id"]
            for ws in self._rooms.get(game_id, set())
            if ws in self._meta
        }

    async def send_personal(self, ws: WebSocket, message: dict[str, Any]) -> None:
        await ws.send_json(message)

    async def broadcast_local(self, game_id: int, message: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(game_id, set())):
            try:
                await ws.send_json(message)
            except Exception:  # pragma: no cover - client vanished mid-send
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def _bridge(self, game_id: int) -> None:
        try:
            async for event in subscribe_room(game_id):
                await self.broadcast_local(game_id, event)
        except asyncio.CancelledError:  # pragma: no cover - cooperative cancel
            raise


manager = ConnectionManager()
