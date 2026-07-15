from pydantic import BaseModel

from app.core.enums import EffectType, TriggerType
from app.schemas.base import ORMModel


class EventCreate(BaseModel):
    scenario_id: int
    name: str = ""
    trigger_type: TriggerType
    trigger_payload: dict = {}
    effect_type: EffectType
    effect_payload: dict = {}
    narration_text: str = ""
    fire_once: bool = True


class EventUpdate(BaseModel):
    name: str | None = None
    trigger_type: TriggerType | None = None
    trigger_payload: dict | None = None
    effect_type: EffectType | None = None
    effect_payload: dict | None = None
    narration_text: str | None = None
    fire_once: bool | None = None


class EventRead(ORMModel):
    id: int
    scenario_id: int
    name: str
    trigger_type: TriggerType
    trigger_payload: dict
    effect_type: EffectType
    effect_payload: dict
    narration_text: str
    fire_once: bool
