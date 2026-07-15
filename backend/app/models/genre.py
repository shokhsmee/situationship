"""Genre — top-level thematic grouping for scenarios (Crime, Ecology, ...)."""
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Genre(Base, TimestampMixin):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str] = mapped_column(String(16), default="#f59e0b", nullable=False)

    scenarios: Mapped[list["Scenario"]] = relationship(  # noqa: F821
        back_populates="genre", cascade="all, delete-orphan"
    )
