"""Location — a place on the scenario map; may be the correct answer."""
from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # Coordinates stored as percentages (0-100) of the map image.
    map_x: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    map_y: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    is_correct_answer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    scenario: Mapped["Scenario"] = relationship(  # noqa: F821
        back_populates="locations", foreign_keys=[scenario_id]
    )
    evidence: Mapped[list["Evidence"]] = relationship(  # noqa: F821
        back_populates="location"
    )
