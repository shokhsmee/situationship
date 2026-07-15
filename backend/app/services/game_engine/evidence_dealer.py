"""Decide which evidence a player owns and may reveal right now (pure)."""
from __future__ import annotations

from collections.abc import Iterable

from app.services.game_engine.types import EvidenceDef


def owned_evidence(evidence: Iterable[EvidenceDef], role_id: int) -> list[EvidenceDef]:
    """All evidence belonging to a role, ordered by reveal round then id."""
    owned = [e for e in evidence if e.role_id == role_id]
    return sorted(owned, key=lambda e: (e.reveal_phase, e.id))


def is_revealable(
    ev: EvidenceDef,
    *,
    current_round: int,
    unlocked_ids: set[int],
    already_revealed_ids: set[int],
) -> bool:
    """A card is revealable when it is unlocked, in-round, and not yet on the board."""
    if ev.id in already_revealed_ids:
        return False
    if ev.starts_locked and ev.id not in unlocked_ids:
        return False
    return ev.reveal_phase <= current_round


def revealable_evidence(
    evidence: Iterable[EvidenceDef],
    role_id: int,
    *,
    current_round: int,
    unlocked_ids: set[int] | None = None,
    already_revealed_ids: set[int] | None = None,
) -> list[EvidenceDef]:
    unlocked_ids = unlocked_ids or set()
    already_revealed_ids = already_revealed_ids or set()
    return [
        e
        for e in owned_evidence(evidence, role_id)
        if is_revealable(
            e,
            current_round=current_round,
            unlocked_ids=unlocked_ids,
            already_revealed_ids=already_revealed_ids,
        )
    ]
