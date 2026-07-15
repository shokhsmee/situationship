"""Game — a live session of a scenario with its runtime state."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import GameOutcome, GamePhase, GameStatus
from app.models.base import Base, TimestampMixin


class Game(Base, TimestampMixin):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id"), index=True, nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus, native_enum=False), default=GameStatus.LOBBY, nullable=False
    )
    current_phase: Mapped[GamePhase] = mapped_column(
        Enum(GamePhase, native_enum=False), default=GamePhase.LOBBY, nullable=False
    )
    current_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phase_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Final answer chosen by the team.
    chosen_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    chosen_answer_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Populated once roles are assigned.
    insider_player_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    outcome: Mapped[GameOutcome | None] = mapped_column(
        Enum(GameOutcome, native_enum=False), nullable=True
    )
    insider_caught: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Host overrides: {"timers": {...}, "insider_enabled": true, "rounds": 2}.
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    scenario: Mapped["Scenario"] = relationship()  # noqa: F821
    players: Mapped[list["GamePlayer"]] = relationship(  # noqa: F821
        back_populates="game", cascade="all, delete-orphan"
    )
    logs: Mapped[list["GameLog"]] = relationship(  # noqa: F821
        back_populates="game", cascade="all, delete-orphan"
    )
