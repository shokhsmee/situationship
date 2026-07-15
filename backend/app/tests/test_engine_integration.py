"""End-to-end engine test against real Postgres + Redis (the seeded demo).

Skipped automatically unless both services are reachable. Run with:
    DATABASE_URL=... REDIS_URL=... pytest app/tests/test_engine_integration.py
Requires the demo scenario to be seeded (python -m app.scripts.seed).
"""
import pytest
from sqlalchemy import select

from app.core.enums import GameOutcome, GamePhase, GameStatus
from app.models import Evidence, Scenario, User

pytestmark = pytest.mark.asyncio


async def _services_available() -> bool:
    try:
        from app.core.redis import redis_client

        await redis_client.ping()
        from app.core.database import engine as db_engine

        async with db_engine.connect():
            return True
    except Exception:
        return False


ZERO_TIMERS = {"intro": 0, "evidence": 0, "discussion": 0, "vote": 0, "insider_guess": 0}


async def _make_users(session, n: int) -> list[User]:
    users = [User(display_name=f"P{i}", username=f"itest_p{i}") for i in range(n)]
    session.add_all(users)
    await session.flush()
    return users


async def test_full_game_investigators_win():
    if not await _services_available():
        pytest.skip("Postgres/Redis not reachable")

    from app.core.database import session_scope
    from app.services.game_engine.engine import GameEngine

    async with session_scope() as session:
        engine = GameEngine(session)
        scenario = await session.scalar(select(Scenario).where(Scenario.title == "City Pollution"))
        assert scenario is not None, "seed the demo scenario first"

        users = await _make_users(session, 5)  # one per role -> all evidence in play
        game = await engine.create_game(
            scenario_id=scenario.id,
            host_user_id=users[0].id,
            settings_override={"timers": ZERO_TIMERS, "rounds": 2, "insider_enabled": True},
        )
        for u in users[1:]:
            await engine.add_player(game, user_id=u.id)

        await engine.start_game(game, by_user_id=users[0].id)
        players = await engine._players(game)
        assert all(p.role_id for p in players), "every player got a role"
        assert game.insider_player_id is not None
        assert game.current_phase == GamePhase.INTRO

        # INTRO -> EVIDENCE (round 1)
        await engine.advance_phase(game)
        assert (game.current_phase, game.current_round) == (GamePhase.EVIDENCE, 1)

        # Reveal the two cards that combine to unlock the hidden pipe photo.
        truck = await session.scalar(
            select(Evidence).where(Evidence.scenario_id == scenario.id, Evidence.title == "Night Truck Log")
        )
        report = await session.scalar(
            select(Evidence).where(
                Evidence.scenario_id == scenario.id, Evidence.title == "Chemical Poisoning Report"
            )
        )
        pipe = await session.scalar(
            select(Evidence).where(
                Evidence.scenario_id == scenario.id, Evidence.title == "Hidden Discharge Pipe Photo"
            )
        )
        p_truck = next(p for p in players if p.role_id == truck.role_id)
        p_report = next(p for p in players if p.role_id == report.role_id)
        await engine.reveal_evidence(game, p_truck, truck.id)
        await engine.reveal_evidence(game, p_report, report.id)

        from app.core.redis import get_state

        unlocked = set(await get_state(game.id, "unlocked_evidence") or [])
        assert pipe.id in unlocked, "combination event should unlock the pipe photo"
        board = set(await get_state(game.id, "board_evidence") or [])
        assert {truck.id, report.id} <= board

        # Per-player secrecy: public state leaks no roles; insider sees a goal.
        pub = await engine.public_state(game)
        assert all("role" not in pl and "is_insider" not in pl for pl in pub["players"])
        insider = next(p for p in players if p.is_insider)
        snap = await engine.player_snapshot(game, insider)
        assert snap["me"]["is_insider"] is True and snap["me"]["insider_goal"]
        outsider = next(p for p in players if not p.is_insider)
        snap2 = await engine.player_snapshot(game, outsider)
        assert snap2["me"]["is_insider"] is False and snap2["me"]["insider_goal"] is None

        # Run to the vote: EVIDENCE1 -> DISCUSSION1 -> EVIDENCE2 -> DISCUSSION2 -> VOTE
        for _ in range(4):
            await engine.advance_phase(game)
        assert game.current_phase == GamePhase.VOTE

        # Everyone votes for the correct location.
        for p in players:
            await engine.cast_vote(game, p, scenario.correct_location_id)

        # VOTE -> INSIDER_GUESS
        await engine.advance_phase(game)
        assert game.current_phase == GamePhase.INSIDER_GUESS
        for p in players:
            if not p.is_insider:
                await engine.guess_insider(game, p, game.insider_player_id)

        # INSIDER_GUESS -> RESULT (finalize runs here)
        await engine.advance_phase(game)
        assert game.status == GameStatus.FINISHED
        assert game.outcome == GameOutcome.INVESTIGATORS_WIN
        assert game.insider_caught is True

        players = await engine._players(game)
        winners = [p for p in players if not p.is_insider]
        assert all(p.score > 0 for p in winners), "investigators scored points"
