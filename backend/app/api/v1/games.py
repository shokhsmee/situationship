"""Game lifecycle: browse scenarios, create/join lobby, start, fetch state."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_engine
from app.models import Game, GamePlayer, Scenario, User
from app.schemas.game import (
    GameCreatedResponse,
    GameCreateRequest,
    GameJoinRequest,
    ScenarioSummary,
)
from app.services.game_engine.engine import EngineError, GameEngine

router = APIRouter()


async def _load_player(session: AsyncSession, game: Game, user_id: int) -> GamePlayer:
    player = await session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id, GamePlayer.user_id == user_id
        )
    )
    if player is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "you are not in this game")
    return player


@router.get("/scenarios", response_model=list[ScenarioSummary])
async def list_scenarios(session: AsyncSession = Depends(get_db)):
    rows = await session.scalars(
        select(Scenario).where(Scenario.is_published.is_(True)).order_by(Scenario.title)
    )
    return list(rows)


@router.post("", response_model=GameCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    body: GameCreateRequest,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    scenario = await engine.session.get(Scenario, body.scenario_id)
    if scenario is None or not scenario.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "scenario not found or unpublished")
    game = await engine.create_game(
        scenario_id=body.scenario_id, host_user_id=user.id, settings_override=body.settings
    )
    await engine.session.commit()
    return GameCreatedResponse(id=game.id, code=game.code)


@router.post("/join")
async def join_game(
    body: GameJoinRequest,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game = await engine.get_game_by_code(body.code)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no game with that code")
    try:
        await engine.add_player(game, user_id=user.id)
    except EngineError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await engine.session.commit()
    player = await _load_player(engine.session, game, user.id)
    return await engine.player_snapshot(game, player)


@router.get("/{game_id}/state")
async def game_state(
    game_id: int,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game = await engine.get_game(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "game not found")
    player = await _load_player(engine.session, game, user.id)
    player.connected = True
    await engine.session.commit()
    return await engine.player_snapshot(game, player)


@router.get("/{game_id}/result")
async def game_result(
    game_id: int,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game = await engine.get_game(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "game not found")
    await _load_player(engine.session, game, user.id)
    return await engine.result_payload(game)


@router.post("/{game_id}/start")
async def start_game(
    game_id: int,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game = await engine.get_game(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "game not found")
    try:
        await engine.start_game(game, by_user_id=user.id)
    except EngineError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await engine.session.commit()
    player = await _load_player(engine.session, game, user.id)
    return await engine.player_snapshot(game, player)
