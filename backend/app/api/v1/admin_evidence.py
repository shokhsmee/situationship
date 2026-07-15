"""Admin: evidence CRUD + role×evidence coverage matrix for balance tuning."""
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_writer
from app.models import Evidence, Role
from app.schemas.evidence import EvidenceCreate, EvidenceRead, EvidenceUpdate

router = APIRouter(dependencies=[Depends(require_writer)])


@router.get("", response_model=list[EvidenceRead])
async def list_evidence(scenario_id: int, session: AsyncSession = Depends(get_db)):
    rows = await session.scalars(
        select(Evidence).where(Evidence.scenario_id == scenario_id).order_by(Evidence.id)
    )
    return list(rows)


@router.get("/coverage", response_model=dict)
async def coverage_matrix(scenario_id: int, session: AsyncSession = Depends(get_db)):
    """Evidence count per role so the writer can see balance at a glance."""
    roles = list(
        await session.scalars(select(Role).where(Role.scenario_id == scenario_id))
    )
    evidence = list(
        await session.scalars(select(Evidence).where(Evidence.scenario_id == scenario_id))
    )
    counts = Counter(e.role_id for e in evidence)
    red_herrings = Counter(e.role_id for e in evidence if e.is_red_herring)
    return {
        "roles": [
            {
                "role_id": r.id,
                "name": r.name,
                "evidence_count": counts.get(r.id, 0),
                "red_herrings": red_herrings.get(r.id, 0),
                "can_be_insider": r.can_be_insider,
            }
            for r in roles
        ],
        "total_evidence": len(evidence),
    }


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
async def create_evidence(body: EvidenceCreate, session: AsyncSession = Depends(get_db)):
    evidence = Evidence(**body.model_dump())
    session.add(evidence)
    await session.commit()
    await session.refresh(evidence)
    return evidence


@router.patch("/{evidence_id}", response_model=EvidenceRead)
async def update_evidence(
    evidence_id: int, body: EvidenceUpdate, session: AsyncSession = Depends(get_db)
):
    evidence = await session.get(Evidence, evidence_id)
    if evidence is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "evidence not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(evidence, field, value)
    await session.commit()
    await session.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(evidence_id: int, session: AsyncSession = Depends(get_db)):
    evidence = await session.get(Evidence, evidence_id)
    if evidence is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "evidence not found")
    await session.delete(evidence)
    await session.commit()
