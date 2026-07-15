"""Role — a character in a scenario, held privately by one player."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(96), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    can_be_insider: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Optional structured ability payload, e.g. {"type": "peek", "uses": 1}.
    special_ability: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    scenario: Mapped["Scenario"] = relationship(back_populates="roles")  # noqa: F821
    evidence: Mapped[list["Evidence"]] = relationship(  # noqa: F821
        back_populates="role"
    )
