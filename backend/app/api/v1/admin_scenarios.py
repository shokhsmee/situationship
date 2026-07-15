"""Admin: scenario CRUD + validation + publish + dashboard stats."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_writer
from app.models import Scenario
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioDetail,
    ScenarioRead,
    ScenarioUpdate,
    ScenarioValidation,
)
from app.services import scenario_service, stats_service

router = APIRouter(dependencies=[Depends(require_writer)])


@router.get("/dashboard", response_model=dict)
async def dashboard(session: AsyncSession = Depends(get_db)):
    return await stats_service.dashboard(session)


@router.get("", response_model=list[ScenarioRead])
async def list_scenarios(session: AsyncSession = Depends(get_db)):
    return list(await session.scalars(select(Scenario).order_by(Scenario.title)))


@router.post("", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(body: ScenarioCreate, session: AsyncSession = Depends(get_db)):
    scenario = Scenario(**body.model_dump())
    session.add(scenario)
    await session.commit()
    await session.refresh(scenario)
    return scenario


@router.get("/{scenario_id}", response_model=ScenarioDetail)
async def get_scenario(scenario_id: int, session: AsyncSession = Depends(get_db)):
    scenario = await scenario_service.load_detail(session, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scenario not found")
    return scenario


@router.patch("/{scenario_id}", response_model=ScenarioRead)
async def update_scenario(
    scenario_id: int, body: ScenarioUpdate, session: AsyncSession = Depends(get_db)
):
    scenario = await session.get(Scenario, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scenario not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(scenario, field, value)
    await session.commit()
    await session.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: int, session: AsyncSession = Depends(get_db)):
    scenario = await session.get(Scenario, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scenario not found")
    await session.delete(scenario)
    await session.commit()


@router.get("/{scenario_id}/validate", response_model=ScenarioValidation)
async def validate_scenario(scenario_id: int, session: AsyncSession = Depends(get_db)):
    return await scenario_service.validate_scenario(session, scenario_id)


@router.post("/{scenario_id}/publish", response_model=ScenarioRead)
async def publish_scenario(scenario_id: int, session: AsyncSession = Depends(get_db)):
    """Validate then publish — refuses to publish an invalid scenario."""
    result = await scenario_service.validate_scenario(session, scenario_id)
    if not result.valid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, {"errors": result.errors})
    scenario = await session.get(Scenario, scenario_id)
    scenario.is_published = True
    await session.commit()
    await session.refresh(scenario)
    return scenario


@router.post("/{scenario_id}/unpublish", response_model=ScenarioRead)
async def unpublish_scenario(scenario_id: int, session: AsyncSession = Depends(get_db)):
    scenario = await session.get(Scenario, scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scenario not found")
    scenario.is_published = False
    await session.commit()
    await session.refresh(scenario)
    return scenario
