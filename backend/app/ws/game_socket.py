"""`/ws/game/{game_id}` endpoint: auth, initial snapshot, presence, router.

Actions that mutate the game (reveal/vote/guess) go through the REST gameplay
API; this socket carries real-time sync only (personal snapshot on connect,
presence, and ephemeral detective-board thread updates).
"""
from __future__ import annotations

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.redis import publish_event
from app.core.security import decode_access_token
from app.models import Game, GamePlayer
from app.services.game_engine.engine import GameEngine
from app.ws.manager import manager

router = APIRouter()


async def _authenticate(token: str | None) -> int | None:
    if not token:
        return None
    try:
        return int(decode_access_token(token)["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


@router.websocket("/ws/game/{game_id}")
async def game_socket(websocket: WebSocket, game_id: int, token: str | None = None):
    user_id = await _authenticate(token)
    if user_id is None:
        await websocket.close(code=4401)
        return

    # Verify membership and grab the player id (short-lived session).
    async with AsyncSessionLocal() as session:
        game = await session.get(Game, game_id)
        if game is None:
            await websocket.close(code=4404)
            return
        player = await session.scalar(
            select(GamePlayer).where(
                GamePlayer.game_id == game_id, GamePlayer.user_id == user_id
            )
        )
        if player is None:
            await websocket.close(code=4403)
            return
        player_id = player.id

    await manager.connect(game_id, websocket, user_id=user_id, player_id=player_id)

    # Mark connected + send this player their private snapshot.
    async with AsyncSessionLocal() as session:
        engine = GameEngine(session)
        game = await engine.get_game(game_id)
        player = await session.get(GamePlayer, player_id)
        player.connected = True
        await session.commit()
        await manager.send_personal(websocket, {
            "type": "snapshot",
            "state": await engine.player_snapshot(game, player),
        })
    await publish_event(game_id, {"type": "presence", "player_id": player_id, "online": True})

    try:
        while True:
            msg = await websocket.receive_json()
            await _route(game_id, player_id, websocket, msg)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
        async with AsyncSessionLocal() as session:
            player = await session.get(GamePlayer, player_id)
            if player:
                player.connected = False
                await session.commit()
        await publish_event(game_id, {"type": "presence", "player_id": player_id, "online": False})


async def _route(game_id: int, player_id: int, websocket: WebSocket, msg: dict) -> None:
    msg_type = msg.get("type")
    if msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    elif msg_type == "sync":
        async with AsyncSessionLocal() as session:
            engine = GameEngine(session)
            game = await engine.get_game(game_id)
            player = await session.get(GamePlayer, player_id)
            if game and player:
                await websocket.send_json(
                    {"type": "snapshot", "state": await engine.player_snapshot(game, player)}
                )
    elif msg_type in {"thread_add", "thread_remove"}:
        # Ephemeral corkboard string between two evidence cards — fan out to room.
        await publish_event(
            game_id,
            {
                "type": msg_type,
                "player_id": player_id,
                "from": msg.get("from"),
                "to": msg.get("to"),
            },
        )
