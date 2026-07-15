"""Aggregate stats for the admin dashboard (games, popularity, win rates)."""
from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import GameOutcome, GameStatus
from app.models import Game, Scenario


async def dashboard(session: AsyncSession) -> dict:
    finished = await session.scalar(
        select(func.count(Game.id)).where(Game.status == GameStatus.FINISHED)
    )
    total = await session.scalar(select(func.count(Game.id)))

    # Games played + investigator win-rate per scenario.
    rows = await session.execute(
        select(
            Scenario.id,
            Scenario.title,
            func.count(Game.id),
            func.sum(case((Game.outcome == GameOutcome.INVESTIGATORS_WIN, 1), else_=0)),
        )
        .join(Game, Game.scenario_id == Scenario.id)
        .where(Game.status == GameStatus.FINISHED)
        .group_by(Scenario.id, Scenario.title)
        .order_by(func.count(Game.id).desc())
    )
    scenarios = []
    for sid, title, played, inv_wins in rows:
        played = played or 0
        inv_wins = inv_wins or 0
        scenarios.append(
            {
                "scenario_id": sid,
                "title": title,
                "games_played": played,
                "investigator_win_rate": round(inv_wins / played, 3) if played else 0.0,
            }
        )

    return {
        "games_total": total or 0,
        "games_finished": finished or 0,
        "scenarios": scenarios,
    }
