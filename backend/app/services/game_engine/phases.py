"""Phase state machine (pure).

Linear flow:
    LOBBY -> INTRO -> (EVIDENCE -> DISCUSSION) x rounds -> VOTE
          -> [INSIDER_GUESS] -> RESULT

The EVENT phase is *reactive*: conditional events fire during EVIDENCE/DISCUSSION
as popups (see event_processor) rather than occupying a fixed slot, so it is not
part of the linear advance() path.
"""
from __future__ import annotations

from app.core.enums import GamePhase

# Phases that carry a per-phase countdown timer.
TIMED_PHASES: frozenset[GamePhase] = frozenset(
    {
        GamePhase.INTRO,
        GamePhase.EVIDENCE,
        GamePhase.DISCUSSION,
        GamePhase.VOTE,
        GamePhase.INSIDER_GUESS,
    }
)


def initial_phase() -> tuple[GamePhase, int]:
    """Phase entered the moment a game starts (round counter not yet begun)."""
    return GamePhase.INTRO, 0


def advance(
    current: GamePhase,
    current_round: int,
    total_rounds: int,
    *,
    insider_enabled: bool = True,
) -> tuple[GamePhase, int]:
    """Return the (phase, round) that follows the current one.

    RESULT is terminal and returns itself.
    """
    total_rounds = max(1, total_rounds)

    if current == GamePhase.LOBBY:
        return GamePhase.INTRO, 0
    if current == GamePhase.INTRO:
        return GamePhase.EVIDENCE, 1
    if current == GamePhase.EVIDENCE:
        return GamePhase.DISCUSSION, current_round
    if current == GamePhase.DISCUSSION:
        if current_round < total_rounds:
            return GamePhase.EVIDENCE, current_round + 1
        return GamePhase.VOTE, current_round
    if current == GamePhase.VOTE:
        return (
            (GamePhase.INSIDER_GUESS, current_round)
            if insider_enabled
            else (GamePhase.RESULT, current_round)
        )
    if current == GamePhase.INSIDER_GUESS:
        return GamePhase.RESULT, current_round
    # EVENT (reactive) or RESULT
    return GamePhase.RESULT, current_round


def is_terminal(phase: GamePhase) -> bool:
    return phase == GamePhase.RESULT
