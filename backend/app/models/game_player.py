"""GamePlayer — a user's seat in a game, holding their private role state."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class GamePlayer(Base, TimestampMixin):
    __tablename__ = "game_players"
    __table_args__ = (UniqueConstraint("game_id", "user_id", name="uq_game_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    is_insider: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_host: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Evidence ids this player has revealed to the shared board.
    revealed_evidence: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # This player's vote for the final answer (location id) and insider guess.
    voted_location_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    guessed_insider_player_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    game: Mapped["Game"] = relationship(back_populates="players")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="game_players")  # noqa: F821
    role: Mapped["Role | None"] = relationship()  # noqa: F821
