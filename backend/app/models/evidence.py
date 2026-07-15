"""Evidence — a private clue owned by a role, revealable to the shared board."""
from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EvidenceType
from app.models.base import Base, TimestampMixin


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(160), nullable=False)
    text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, native_enum=False),
        default=EvidenceType.DOCUMENT,
        nullable=False,
    )
    is_red_herring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # 1-based round in which this evidence becomes revealable.
    reveal_phase: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # How strongly this points at the truth (used for scoring / balance hints).
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Evidence unlocked dynamically by an event starts locked.
    starts_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scenario: Mapped["Scenario"] = relationship(back_populates="evidence")  # noqa: F821
    role: Mapped["Role"] = relationship(back_populates="evidence")  # noqa: F821
    location: Mapped["Location | None"] = relationship(  # noqa: F821
        back_populates="evidence"
    )
