from pydantic import BaseModel


class RevealEvidenceRequest(BaseModel):
    evidence_id: int


class VoteRequest(BaseModel):
    location_id: int


class InsiderGuessRequest(BaseModel):
    target_player_id: int


class ActionResponse(BaseModel):
    ok: bool = True
    detail: str | None = None
