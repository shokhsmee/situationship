"""Cross-cutting enumerations shared by models, schemas and the game engine.

Kept in core (not in a model file) because several layers depend on them and we
never want a model->model import just to reach an enum.
"""
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    WRITER = "writer"
    PLAYER = "player"


class GameStatus(StrEnum):
    LOBBY = "lobby"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABORTED = "aborted"


class GamePhase(StrEnum):
    """Ordered phases of the state machine (see services/game_engine/phases.py)."""

    LOBBY = "lobby"
    INTRO = "intro"
    EVIDENCE = "evidence"
    DISCUSSION = "discussion"
    EVENT = "event"
    VOTE = "vote"
    INSIDER_GUESS = "insider_guess"
    RESULT = "result"


class EvidenceType(StrEnum):
    DOCUMENT = "document"
    WITNESS = "witness"
    PHYSICAL = "physical"
    MEDICAL = "medical"
    RUMOR = "rumor"


class TriggerType(StrEnum):
    EVIDENCE_REVEALED = "evidence_revealed"
    EVIDENCE_COMBINED = "evidence_combined"
    LOCATION_VISITED = "location_visited"
    PHASE_STARTED = "phase_started"
    VOTE_RESULT = "vote_result"


class EffectType(StrEnum):
    UNLOCK_EVIDENCE = "unlock_evidence"
    LOCK_EVIDENCE = "lock_evidence"
    ADD_TIME = "add_time"
    REMOVE_TIME = "remove_time"
    REVEAL_HINT = "reveal_hint"
    NEW_SITUATION_TEXT = "new_situation_text"
    SWAP_ROLE_INFO = "swap_role_info"


class GameOutcome(StrEnum):
    INVESTIGATORS_WIN = "investigators_win"
    INSIDER_WIN = "insider_win"
    UNRESOLVED = "unresolved"
