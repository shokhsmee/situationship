from pydantic import BaseModel

from app.schemas.base import ORMModel
from app.schemas.evidence import EvidenceRead
from app.schemas.event import EventRead
from app.schemas.location import LocationRead
from app.schemas.role import RoleRead


class ScenarioCreate(BaseModel):
    genre_id: int
    title: str
    intro_text: str = ""
    task_text: str = ""
    difficulty: int = 1
    min_players: int = 3
    max_players: int = 8
    cover_image: str | None = None
    map_image: str | None = None
    rounds: int = 2
    timers: dict = {}
    truth_story: str = ""


class ScenarioUpdate(BaseModel):
    genre_id: int | None = None
    title: str | None = None
    intro_text: str | None = None
    task_text: str | None = None
    difficulty: int | None = None
    min_players: int | None = None
    max_players: int | None = None
    cover_image: str | None = None
    map_image: str | None = None
    rounds: int | None = None
    timers: dict | None = None
    correct_location_id: int | None = None
    correct_answer_text: str | None = None
    truth_story: str | None = None
    is_published: bool | None = None


class ScenarioRead(ORMModel):
    id: int
    genre_id: int
    title: str
    intro_text: str
    task_text: str
    difficulty: int
    min_players: int
    max_players: int
    cover_image: str | None
    map_image: str | None
    rounds: int
    timers: dict
    correct_location_id: int | None
    correct_answer_text: str | None
    truth_story: str
    is_published: bool


class ScenarioDetail(ScenarioRead):
    """Full authoring payload for the Scenario Studio."""

    locations: list[LocationRead] = []
    roles: list[RoleRead] = []
    evidence: list[EvidenceRead] = []
    events: list[EventRead] = []


class ScenarioValidation(BaseModel):
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
