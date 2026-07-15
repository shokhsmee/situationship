"""Conditional event engine (pure).

Given the events of a scenario and the current game state, decide which events
fire now and normalise their effects into `TriggeredEffect`s the orchestrator can
apply.
"""
from __future__ import annotations

from collections.abc import Iterable

from app.core.enums import EffectType, TriggerType
from app.services.game_engine.types import EventDef, TriggeredEffect

# Effects that grant/remove time — the sign is derived from the effect type.
_TIME_EFFECTS = {EffectType.ADD_TIME: 1, EffectType.REMOVE_TIME: -1}


def _matches(event: EventDef, ctx: "EventContext") -> bool:
    payload = event.trigger_payload or {}
    ids = set(payload.get("evidence_ids", []))

    match event.trigger_type:
        case TriggerType.EVIDENCE_REVEALED:
            # Any listed evidence now on the board.
            return bool(ids & ctx.revealed_evidence_ids)
        case TriggerType.EVIDENCE_COMBINED:
            # Every listed evidence on the board simultaneously.
            return bool(ids) and ids.issubset(ctx.revealed_evidence_ids)
        case TriggerType.LOCATION_VISITED:
            return payload.get("location_id") in ctx.visited_location_ids
        case TriggerType.PHASE_STARTED:
            return payload.get("phase") == ctx.phase
        case TriggerType.VOTE_RESULT:
            return payload.get("location_id") == ctx.vote_location_id
    return False


def _to_effect(event: EventDef) -> TriggeredEffect:
    payload = event.effect_payload or {}
    unlocked = tuple(payload.get("evidence_ids", []))
    seconds = int(payload.get("seconds", 0)) * _TIME_EFFECTS.get(event.effect_type, 0)
    return TriggeredEffect(
        event_id=event.id,
        effect_type=event.effect_type,
        effect_payload=payload,
        narration_text=event.narration_text,
        unlocked_evidence_ids=unlocked,
        seconds_delta=seconds,
    )


class EventContext:
    """Snapshot of everything an event trigger may inspect."""

    __slots__ = ("revealed_evidence_ids", "visited_location_ids", "phase", "vote_location_id")

    def __init__(
        self,
        *,
        revealed_evidence_ids: set[int] | None = None,
        visited_location_ids: set[int] | None = None,
        phase: str | None = None,
        vote_location_id: int | None = None,
    ) -> None:
        self.revealed_evidence_ids = revealed_evidence_ids or set()
        self.visited_location_ids = visited_location_ids or set()
        self.phase = phase
        self.vote_location_id = vote_location_id


def evaluate_events(
    events: Iterable[EventDef],
    ctx: EventContext,
    *,
    fired_event_ids: set[int] | None = None,
) -> list[TriggeredEffect]:
    """Return effects for every event whose trigger is satisfied and not spent."""
    fired_event_ids = fired_event_ids or set()
    triggered: list[TriggeredEffect] = []
    for event in events:
        if event.fire_once and event.id in fired_event_ids:
            continue
        if _matches(event, ctx):
            triggered.append(_to_effect(event))
    return triggered
