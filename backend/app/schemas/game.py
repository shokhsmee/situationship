from pydantic import BaseModel


class GameCreateRequest(BaseModel):
    scenario_id: int
    settings: dict = {}


class GameJoinRequest(BaseModel):
    code: str


class GameCreatedResponse(BaseModel):
    id: int
    code: str


class ScenarioSummary(BaseModel):
    """Lightweight scenario card for lobby/browse screens."""

    id: int
    title: str
    genre_id: int
    difficulty: int
    min_players: int
    max_players: int
    cover_image: str | None = None
