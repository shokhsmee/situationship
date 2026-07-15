"""Admin: role CRUD."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_writer
from app.models import Role
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(dependencies=[Depends(require_writer)])


@router.get("", response_model=list[RoleRead])
async def list_roles(scenario_id: int, session: AsyncSession = Depends(get_db)):
    rows = await session.scalars(
        select(Role).where(Role.scenario_id == scenario_id).order_by(Role.id)
    )
    return list(rows)


@router.post("", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(body: RoleCreate, session: AsyncSession = Depends(get_db)):
    role = Role(**body.model_dump())
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(role_id: int, body: RoleUpdate, session: AsyncSession = Depends(get_db)):
    role = await session.get(Role, role_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "role not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    await session.commit()
    await session.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, session: AsyncSession = Depends(get_db)):
    role = await session.get(Role, role_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "role not found")
    await session.delete(role)
    await session.commit()
