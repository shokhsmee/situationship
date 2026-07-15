"""Authentication: classic credentials + Telegram Mini App initData."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    validate_telegram_init_data,
    verify_password,
)
from app.models import User
from app.schemas.auth import (
    BotAuthRequest,
    LoginRequest,
    RegisterRequest,
    TelegramAuthRequest,
    TokenResponse,
)
from app.schemas.user import UserRead

router = APIRouter()


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, {"role": user.role.value}),
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_db)):
    exists = await session.scalar(select(User).where(User.username == body.username))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "username already taken")
    user = User(
        username=body.username,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
        language=body.language,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_db)):
    user = await session.scalar(select(User).where(User.username == body.username))
    if user is None or not user.hashed_password or not verify_password(
        body.password, user.hashed_password
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    return _token_response(user)


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(body: TelegramAuthRequest, session: AsyncSession = Depends(get_db)):
    tg_user = validate_telegram_init_data(body.init_data)
    if tg_user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid Telegram init data")

    tg_id = int(tg_user["id"])
    user = await session.scalar(select(User).where(User.telegram_id == tg_id))
    if user is None:
        user = User(
            telegram_id=tg_id,
            username=tg_user.get("username"),
            display_name=tg_user.get("first_name") or tg_user.get("username") or f"tg{tg_id}",
            language=tg_user.get("language_code", "en"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return _token_response(user)


@router.post("/bot", response_model=TokenResponse)
async def bot_auth(body: BotAuthRequest, session: AsyncSession = Depends(get_db)):
    """Trusted server-to-server auth for the Telegram bot (verifies bot token)."""
    import hmac

    if not settings.telegram_bot_token or not hmac.compare_digest(
        body.bot_token, settings.telegram_bot_token
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid bot token")

    user = await session.scalar(select(User).where(User.telegram_id == body.telegram_id))
    if user is None:
        user = User(
            telegram_id=body.telegram_id,
            username=body.username,
            display_name=body.first_name or body.username or f"tg{body.telegram_id}",
            language=body.language_code,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return _token_response(user)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user
