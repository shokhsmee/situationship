"""Admin: conditional-event CRUD (the visual IF/THEN builder's backend)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_writer
from app.models import Event
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(dependencies=[Depends(require_writer)])


@router.get("", response_model=list[EventRead])
async def list_events(scenario_id: int, session: AsyncSession = Depends(get_db)):
    rows = await session.scalars(
        select(Event).where(Event.scenario_id == scenario_id).order_by(Event.id)
    )
    return list(rows)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(body: EventCreate, session: AsyncSession = Depends(get_db)):
    event = Event(**body.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(event_id: int, body: EventUpdate, session: AsyncSession = Depends(get_db)):
    event = await session.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "event not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    await session.commit()
    await session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, session: AsyncSession = Depends(get_db)):
    event = await session.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "event not found")
    await session.delete(event)
    await session.commit()
