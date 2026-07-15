"""Scenario — an authored case. Owns locations, roles, evidence and events."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Scenario(Base, TimestampMixin):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    intro_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    task_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    min_players: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    map_image: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Correct answer: either a location on the map or a free-text answer.
    correct_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", use_alter=True, name="fk_scenario_correct_location"),
        nullable=True,
    )
    correct_answer_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    truth_story: Mapped[str] = mapped_column(Text, default="", nullable=False)

    rounds: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    # Per-phase timer overrides (seconds). Falls back to settings defaults.
    timers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    genre: Mapped["Genre"] = relationship(back_populates="scenarios")  # noqa: F821
    locations: Mapped[list["Location"]] = relationship(  # noqa: F821
        back_populates="scenario",
        cascade="all, delete-orphan",
        foreign_keys="Location.scenario_id",
    )
    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        back_populates="scenario", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["Evidence"]] = relationship(  # noqa: F821
        back_populates="scenario", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(  # noqa: F821
        back_populates="scenario", cascade="all, delete-orphan"
    )
    correct_location: Mapped["Location | None"] = relationship(  # noqa: F821
        foreign_keys=[correct_location_id], post_update=True
    )
