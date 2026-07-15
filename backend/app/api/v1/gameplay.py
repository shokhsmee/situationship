"""In-game actions: reveal evidence, vote, guess the insider, advance phase."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import get_current_user, get_engine
from app.models import Game, GamePlayer, User
from app.schemas.gameplay import (
    ActionResponse,
    InsiderGuessRequest,
    RevealEvidenceRequest,
    VoteRequest,
)
from app.services.game_engine.engine import EngineError, GameEngine

router = APIRouter()


async def _game_and_player(engine: GameEngine, game_id: int, user_id: int) -> tuple[Game, GamePlayer]:
    game = await engine.get_game(game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "game not found")
    player = await engine.session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id, GamePlayer.user_id == user_id
        )
    )
    if player is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "you are not in this game")
    return game, player


@router.post("/{game_id}/reveal", response_model=ActionResponse)
async def reveal_evidence(
    game_id: int,
    body: RevealEvidenceRequest,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game, player = await _game_and_player(engine, game_id, user.id)
    try:
        await engine.reveal_evidence(game, player, body.evidence_id)
    except EngineError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await engine.session.commit()
    return ActionResponse()


@router.post("/{game_id}/vote", response_model=ActionResponse)
async def cast_vote(
    game_id: int,
    body: VoteRequest,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game, player = await _game_and_player(engine, game_id, user.id)
    try:
        await engine.cast_vote(game, player, body.location_id)
    except EngineError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await engine.session.commit()
    return ActionResponse()


@router.post("/{game_id}/insider-guess", response_model=ActionResponse)
async def guess_insider(
    game_id: int,
    body: InsiderGuessRequest,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    game, player = await _game_and_player(engine, game_id, user.id)
    try:
        await engine.guess_insider(game, player, body.target_player_id)
    except EngineError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    await engine.session.commit()
    return ActionResponse()


@router.post("/{game_id}/advance", response_model=ActionResponse)
async def advance_phase(
    game_id: int,
    user: User = Depends(get_current_user),
    engine: GameEngine = Depends(get_engine),
):
    """Host-triggered manual phase advance (skip the timer)."""
    game, player = await _game_and_player(engine, game_id, user.id)
    if not player.is_host:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "only the host can advance the phase")
    await engine.advance_phase(game, reason="host")
    await engine.session.commit()
    return ActionResponse()
