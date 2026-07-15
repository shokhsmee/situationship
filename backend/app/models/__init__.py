"""Import every model so it registers on Base.metadata (Alembic + create_all)."""
from app.models.base import Base
from app.models.evidence import Evidence
from app.models.event import Event
from app.models.game import Game
from app.models.game_log import GameLog
from app.models.game_player import GamePlayer
from app.models.genre import Genre
from app.models.location import Location
from app.models.role import Role
from app.models.scenario import Scenario
from app.models.user import User

__all__ = [
    "Base",
    "Evidence",
    "Event",
    "Game",
    "GameLog",
    "GamePlayer",
    "Genre",
    "Location",
    "Role",
    "Scenario",
    "User",
]
