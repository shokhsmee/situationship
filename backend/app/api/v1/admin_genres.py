"""Admin: genre CRUD (admin role only)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Genre
from app.schemas.genre import GenreCreate, GenreRead, GenreUpdate

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=list[GenreRead])
async def list_genres(session: AsyncSession = Depends(get_db)):
    return list(await session.scalars(select(Genre).order_by(Genre.name)))


@router.post("", response_model=GenreRead, status_code=status.HTTP_201_CREATED)
async def create_genre(body: GenreCreate, session: AsyncSession = Depends(get_db)):
    genre = Genre(**body.model_dump())
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.patch("/{genre_id}", response_model=GenreRead)
async def update_genre(genre_id: int, body: GenreUpdate, session: AsyncSession = Depends(get_db)):
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "genre not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(genre, field, value)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, session: AsyncSession = Depends(get_db)):
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "genre not found")
    await session.delete(genre)
    await session.commit()
