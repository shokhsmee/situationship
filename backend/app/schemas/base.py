"""Shared Pydantic base — all read schemas load straight from ORM rows."""
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
