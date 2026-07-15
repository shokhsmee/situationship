"""Event — a conditional rule: IF trigger THEN effect + narration."""
from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EffectType, TriggerType
from app.models.base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), default="", nullable=False)

    trigger_type: Mapped[TriggerType] = mapped_column(
        Enum(TriggerType, native_enum=False), nullable=False
    )
    # e.g. {"evidence_ids": [3, 7]} for EVIDENCE_COMBINED, {"phase": "vote"} etc.
    trigger_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    effect_type: Mapped[EffectType] = mapped_column(
        Enum(EffectType, native_enum=False), nullable=False
    )
    # e.g. {"evidence_ids": [11]} or {"seconds": 60} or {"text": "..."}.
    effect_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    narration_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    fire_once: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    scenario: Mapped["Scenario"] = relationship(back_populates="events")  # noqa: F821
