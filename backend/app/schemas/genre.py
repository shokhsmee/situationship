from pydantic import BaseModel

from app.schemas.base import ORMModel


class GenreCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    color: str = "#f59e0b"


class GenreUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None


class GenreRead(ORMModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    color: str
