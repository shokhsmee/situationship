"""Lightweight, immutable data contracts for the pure engine modules.

Deliberately decoupled from SQLAlchemy so rule logic can be tested with plain
constructor calls. `engine.py` maps ORM rows onto these.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.enums import EffectType, GameOutcome, TriggerType


@dataclass(frozen=True)
class RoleDef:
    id: int
    name: str
    can_be_insider: bool


@dataclass(frozen=True)
class EvidenceDef:
    id: int
    role_id: int
    reveal_phase: int  # 1-based round in which it becomes revealable
    starts_locked: bool
    weight: int
    is_red_herring: bool
    location_id: int | None = None


@dataclass(frozen=True)
class EventDef:
    id: int
    trigger_type: TriggerType
    trigger_payload: dict
    effect_type: EffectType
    effect_payload: dict
    narration_text: str = ""
    fire_once: bool = True


@dataclass(frozen=True)
class RoleAssignment:
    player_id: int
    role_id: int
    is_insider: bool


@dataclass(frozen=True)
class TriggeredEffect:
    event_id: int
    effect_type: EffectType
    effect_payload: dict
    narration_text: str
    # Convenience: evidence ids / seconds pulled out of the payload.
    unlocked_evidence_ids: tuple[int, ...] = ()
    seconds_delta: int = 0


@dataclass
class PlayerScore:
    player_id: int
    is_insider: bool
    base: int = 0
    contribution: int = 0
    bonus: int = 0

    @property
    def total(self) -> int:
        return self.base + self.contribution + self.bonus


@dataclass
class ScoreResult:
    outcome: GameOutcome
    insider_caught: bool
    scores: list[PlayerScore] = field(default_factory=list)
