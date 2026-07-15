"""Server-authoritative phase timers, backed by Redis.

The deadline is the single source of truth (stored in Redis so any worker can
read it and clients can render a synced countdown). A per-game asyncio task
watches the deadline and invokes `on_expire` when it passes. Because the loop
re-reads the deadline every tick, `add_time`/`remove_time` effects and manual
phase advances take effect immediately.
"""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

from app.core.redis import get_state, set_state

TICK_SECONDS = 1.0
ExpireCallback = Callable[[int], Awaitable[None]]


def now() -> float:
    return time.time()


class PhaseTimer:
    """Owns one watcher task per active game."""

    def __init__(self) -> None:
        self._tasks: dict[int, asyncio.Task] = {}

    async def start(self, game_id: int, deadline_ts: float, on_expire: ExpireCallback) -> None:
        await set_state(game_id, "phase_deadline", deadline_ts)
        self.cancel(game_id)
        self._tasks[game_id] = asyncio.create_task(self._watch(game_id, on_expire))

    async def extend(self, game_id: int, seconds: int) -> float | None:
        """Shift the current deadline by `seconds` (may be negative). Returns new ts."""
        deadline = await get_state(game_id, "phase_deadline")
        if deadline is None:
            return None
        new_deadline = float(deadline) + seconds
        await set_state(game_id, "phase_deadline", new_deadline)
        return new_deadline

    def cancel(self, game_id: int) -> None:
        """Cancel the watcher for a game — but never cancel/pop the caller itself.

        `on_expire` runs inside the watcher task and may re-enter `start()`; in
        that case the current task is about to finish on its own, so we leave it.
        """
        task = self._tasks.get(game_id)
        if task is None or task is asyncio.current_task():
            return
        self._tasks.pop(game_id, None)
        if not task.done():
            task.cancel()

    async def _watch(self, game_id: int, on_expire: ExpireCallback) -> None:
        try:
            while True:
                deadline = await get_state(game_id, "phase_deadline")
                if deadline is None:
                    return
                remaining = float(deadline) - now()
                if remaining <= 0:
                    await set_state(game_id, "phase_deadline", None)
                    await on_expire(game_id)
                    return
                await asyncio.sleep(min(remaining, TICK_SECONDS))
        except asyncio.CancelledError:  # pragma: no cover - cooperative cancel
            raise
        finally:
            # Only clear our slot if a fresh timer hasn't already replaced us.
            if self._tasks.get(game_id) is asyncio.current_task():
                self._tasks.pop(game_id, None)


# Module-level singleton shared across the app.
phase_timer = PhaseTimer()
