from pydantic import BaseModel

from app.schemas.base import ORMModel


class RoleCreate(BaseModel):
    scenario_id: int
    name: str
    description: str | None = None
    icon: str | None = None
    can_be_insider: bool = True
    special_ability: dict | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    can_be_insider: bool | None = None
    special_ability: dict | None = None


class RoleRead(ORMModel):
    id: int
    scenario_id: int
    name: str
    description: str | None
    icon: str | None
    can_be_insider: bool
    special_ability: dict | None
