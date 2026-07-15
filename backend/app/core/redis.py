"""Redis client + pub/sub helpers.

Two responsibilities, kept separate from game logic:
  * `redis_client` — authoritative volatile game state (phase, deadlines,
    per-player caches) so a client refresh can be rehydrated.
  * pub/sub — fan-out of room events across API/WS worker processes.
"""
import json
from collections.abc import AsyncIterator
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


def room_channel(game_id: int) -> str:
    return f"game:{game_id}:events"


async def publish_event(game_id: int, event: dict[str, Any]) -> None:
    """Publish a room event to all subscribed WS workers."""
    await redis_client.publish(room_channel(game_id), json.dumps(event))


async def subscribe_room(game_id: int) -> AsyncIterator[dict[str, Any]]:
    """Yield decoded events published to a game room until cancelled."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(room_channel(game_id))
    try:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            yield json.loads(message["data"])
    finally:
        await pubsub.unsubscribe(room_channel(game_id))
        await pubsub.close()


# --- Volatile state helpers (namespaced hashes per game) -------------------

def _state_key(game_id: int) -> str:
    return f"game:{game_id}:state"


async def set_state(game_id: int, field: str, value: Any) -> None:
    await redis_client.hset(_state_key(game_id), field, json.dumps(value))


async def get_state(game_id: int, field: str) -> Any | None:
    raw = await redis_client.hget(_state_key(game_id), field)
    return json.loads(raw) if raw is not None else None


async def get_all_state(game_id: int) -> dict[str, Any]:
    raw = await redis_client.hgetall(_state_key(game_id))
    return {k: json.loads(v) for k, v in raw.items()}


async def clear_state(game_id: int) -> None:
    await redis_client.delete(_state_key(game_id))
