from pydantic import BaseModel

from app.core.enums import EvidenceType
from app.schemas.base import ORMModel


class EvidenceCreate(BaseModel):
    scenario_id: int
    role_id: int
    location_id: int | None = None
    title: str
    text: str = ""
    image: str | None = None
    type: EvidenceType = EvidenceType.DOCUMENT
    is_red_herring: bool = False
    reveal_phase: int = 1
    weight: int = 1
    starts_locked: bool = False


class EvidenceUpdate(BaseModel):
    role_id: int | None = None
    location_id: int | None = None
    title: str | None = None
    text: str | None = None
    image: str | None = None
    type: EvidenceType | None = None
    is_red_herring: bool | None = None
    reveal_phase: int | None = None
    weight: int | None = None
    starts_locked: bool | None = None


class EvidenceRead(ORMModel):
    id: int
    scenario_id: int
    role_id: int
    location_id: int | None
    title: str
    text: str
    image: str | None
    type: EvidenceType
    is_red_herring: bool
    reveal_phase: int
    weight: int
    starts_locked: bool
