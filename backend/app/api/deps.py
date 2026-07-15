"""Shared FastAPI dependencies: DB session, current user, role guards, engine."""
from collections.abc import AsyncGenerator, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.enums import UserRole
from app.core.security import decode_access_token
from app.models import User
from app.services.game_engine.engine import GameEngine

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from exc
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return user


def require_roles(*roles: UserRole) -> Callable:
    async def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "insufficient privileges")
        return user

    return _guard


# Admins and writers may author scenarios; only admins manage genres.
require_writer = require_roles(UserRole.ADMIN, UserRole.WRITER)
require_admin = require_roles(UserRole.ADMIN)


async def get_engine(session: AsyncSession = Depends(get_db)) -> GameEngine:
    return GameEngine(session)
