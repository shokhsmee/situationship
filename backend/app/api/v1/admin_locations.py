"""Admin: location CRUD (map pins for the Scenario Studio)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_writer
from app.models import Location
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate

router = APIRouter(dependencies=[Depends(require_writer)])


@router.get("", response_model=list[LocationRead])
async def list_locations(scenario_id: int, session: AsyncSession = Depends(get_db)):
    rows = await session.scalars(
        select(Location).where(Location.scenario_id == scenario_id).order_by(Location.id)
    )
    return list(rows)


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(body: LocationCreate, session: AsyncSession = Depends(get_db)):
    location = Location(**body.model_dump())
    session.add(location)
    await session.commit()
    await session.refresh(location)
    return location


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int, body: LocationUpdate, session: AsyncSession = Depends(get_db)
):
    location = await session.get(Location, location_id)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "location not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    await session.commit()
    await session.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(location_id: int, session: AsyncSession = Depends(get_db)):
    location = await session.get(Location, location_id)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "location not found")
    await session.delete(location)
    await session.commit()
