from pydantic import BaseModel

from app.schemas.base import ORMModel


class LocationCreate(BaseModel):
    scenario_id: int
    name: str
    description: str | None = None
    image: str | None = None
    map_x: float = 50.0
    map_y: float = 50.0
    is_correct_answer: bool = False


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    image: str | None = None
    map_x: float | None = None
    map_y: float | None = None
    is_correct_answer: bool | None = None


class LocationRead(ORMModel):
    id: int
    scenario_id: int
    name: str
    description: str | None
    image: str | None
    map_x: float
    map_y: float
    is_correct_answer: bool
