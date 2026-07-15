"""Game orchestrator — the only engine module that performs IO.

Responsibilities:
  * map ORM rows into the pure dataclasses,
  * delegate every rule decision to the pure modules,
  * persist authoritative state (DB + Redis) and broadcast non-secret events.

Secret state (a player's role, their private cards, the insider flag) is NEVER
broadcast; it is delivered only to the owning player via `player_snapshot`.
"""
from __future__ import annotations

import secrets
from collections import Counter
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.enums import GameOutcome, GamePhase, GameStatus
from app.core.redis import get_state, publish_event, set_state
from app.models import Evidence, Event, Game, GameLog, GamePlayer, Location, Role, Scenario
from app.services.game_engine import evidence_dealer, phases, role_assigner, scoring
from app.services.game_engine.event_processor import EventContext, evaluate_events
from app.services.game_engine.phases import TIMED_PHASES
from app.services.game_engine.timer import now, phase_timer
from app.services.game_engine.types import EventDef, EvidenceDef, RoleDef

_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no ambiguous chars


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


class EngineError(Exception):
    """Raised for invalid gameplay actions (mapped to HTTP 400 in the API)."""


class GameEngine:
    """Drives one game. Construct per request with the active DB session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -- Loading helpers ----------------------------------------------------

    async def get_game(self, game_id: int) -> Game | None:
        return await self.session.get(Game, game_id)

    async def get_game_by_code(self, code: str) -> Game | None:
        return await self.session.scalar(select(Game).where(Game.code == code.upper()))

    async def _players(self, game: Game) -> list[GamePlayer]:
        return list(
            await self.session.scalars(
                select(GamePlayer).where(GamePlayer.game_id == game.id)
            )
        )

    async def _role_defs(self, scenario_id: int) -> list[RoleDef]:
        rows = await self.session.scalars(select(Role).where(Role.scenario_id == scenario_id))
        return [RoleDef(id=r.id, name=r.name, can_be_insider=r.can_be_insider) for r in rows]

    async def _evidence_defs(self, scenario_id: int) -> list[EvidenceDef]:
        rows = await self.session.scalars(
            select(Evidence).where(Evidence.scenario_id == scenario_id)
        )
        return [
            EvidenceDef(
                id=e.id,
                role_id=e.role_id,
                reveal_phase=e.reveal_phase,
                starts_locked=e.starts_locked,
                weight=e.weight,
                is_red_herring=e.is_red_herring,
                location_id=e.location_id,
            )
            for e in rows
        ]

    async def _event_defs(self, scenario_id: int) -> list[EventDef]:
        rows = await self.session.scalars(select(Event).where(Event.scenario_id == scenario_id))
        return [
            EventDef(
                id=ev.id,
                trigger_type=ev.trigger_type,
                trigger_payload=ev.trigger_payload,
                effect_type=ev.effect_type,
                effect_payload=ev.effect_payload,
                narration_text=ev.narration_text,
                fire_once=ev.fire_once,
            )
            for ev in rows
        ]

    # -- Config helpers -----------------------------------------------------

    def _rounds(self, game: Game, scenario: Scenario) -> int:
        return int(game.settings.get("rounds", scenario.rounds or settings.default_rounds))

    def _insider_enabled(self, game: Game) -> bool:
        return bool(game.settings.get("insider_enabled", True))

    def _phase_duration(self, game: Game, scenario: Scenario, phase: GamePhase) -> int:
        overrides = {**(scenario.timers or {}), **(game.settings.get("timers") or {})}
        defaults = {
            GamePhase.INTRO: settings.default_intro_seconds,
            GamePhase.EVIDENCE: settings.default_evidence_seconds,
            GamePhase.DISCUSSION: settings.default_discussion_seconds,
            GamePhase.VOTE: settings.default_vote_seconds,
            GamePhase.INSIDER_GUESS: settings.default_vote_seconds,
        }
        return int(overrides.get(phase.value, defaults.get(phase, 0)))

    # -- Lobby lifecycle ----------------------------------------------------

    async def create_game(
        self, *, scenario_id: int, host_user_id: int, settings_override: dict | None = None
    ) -> Game:
        code = generate_code()
        while await self.get_game_by_code(code):
            code = generate_code()
        game = Game(
            code=code,
            scenario_id=scenario_id,
            created_by=host_user_id,
            status=GameStatus.LOBBY,
            current_phase=GamePhase.LOBBY,
            settings=settings_override or {},
        )
        self.session.add(game)
        await self.session.flush()
        await self.add_player(game, user_id=host_user_id, is_host=True)
        return game

    async def add_player(self, game: Game, *, user_id: int, is_host: bool = False) -> GamePlayer:
        if game.status != GameStatus.LOBBY:
            raise EngineError("game already started")
        existing = await self.session.scalar(
            select(GamePlayer).where(
                GamePlayer.game_id == game.id, GamePlayer.user_id == user_id
            )
        )
        if existing:
            existing.connected = True
            return existing
        players = await self._players(game)
        scenario = await self.session.get(Scenario, game.scenario_id)
        if scenario and len(players) >= scenario.max_players:
            raise EngineError("lobby is full")
        player = GamePlayer(
            game_id=game.id, user_id=user_id, is_host=is_host, connected=True
        )
        self.session.add(player)
        await self.session.flush()
        await publish_event(game.id, {"type": "player_joined", "player_id": player.id})
        return player

    # -- Start & phase transitions -----------------------------------------

    async def start_game(self, game: Game, *, by_user_id: int) -> None:
        if game.status != GameStatus.LOBBY:
            raise EngineError("game already started")
        players = await self._players(game)
        host = next((p for p in players if p.is_host), None)
        if host and host.user_id != by_user_id:
            raise EngineError("only the host can start the game")
        scenario = await self.session.get(Scenario, game.scenario_id)
        if scenario and len(players) < scenario.min_players:
            raise EngineError(f"need at least {scenario.min_players} players")

        role_defs = await self._role_defs(game.scenario_id)
        assignments = role_assigner.assign_roles(
            [p.id for p in players],
            role_defs,
            insider_enabled=self._insider_enabled(game),
        )
        by_player = {a.player_id: a for a in assignments}
        for p in players:
            a = by_player[p.id]
            p.role_id = a.role_id
            p.is_insider = a.is_insider
            p.revealed_evidence = []
            if a.is_insider:
                game.insider_player_id = p.id

        game.status = GameStatus.IN_PROGRESS
        # Reset volatile round state.
        await set_state(game.id, "board_evidence", [])
        await set_state(game.id, "unlocked_evidence", [])
        await set_state(game.id, "fired_events", [])
        await self._log(game, None, "game_started", {"players": len(players)})

        phase, rnd = phases.initial_phase()
        await self._enter_phase(game, phase, rnd)

    async def _enter_phase(self, game: Game, phase: GamePhase, rnd: int) -> None:
        scenario = await self.session.get(Scenario, game.scenario_id)
        game.current_phase = phase
        game.current_round = rnd

        deadline_ts: float | None = None
        duration = self._phase_duration(game, scenario, phase)
        if phase in TIMED_PHASES and duration > 0:
            deadline_ts = now() + duration
            game.phase_deadline = datetime.fromtimestamp(deadline_ts, tz=UTC)
            await phase_timer.start(game.id, deadline_ts, on_phase_timeout)
        else:
            game.phase_deadline = None
            phase_timer.cancel(game.id)
            await set_state(game.id, "phase_deadline", None)

        await self._log(game, None, "phase_changed", {"phase": phase.value, "round": rnd})
        await publish_event(
            game.id,
            {
                "type": "phase_changed",
                "phase": phase.value,
                "round": rnd,
                "deadline": deadline_ts,
            },
        )

        # PHASE_STARTED conditional events.
        board = set(await get_state(game.id, "board_evidence") or [])
        await self._process_events(
            game, EventContext(phase=phase.value, revealed_evidence_ids=board)
        )

        if phase == GamePhase.RESULT:
            await self.finalize(game)

    async def advance_phase(self, game: Game, *, reason: str = "manual") -> None:
        if game.status != GameStatus.IN_PROGRESS:
            return
        scenario = await self.session.get(Scenario, game.scenario_id)
        nxt, rnd = phases.advance(
            game.current_phase,
            game.current_round,
            self._rounds(game, scenario),
            insider_enabled=self._insider_enabled(game),
        )
        await self._log(game, None, "phase_advance", {"reason": reason})
        await self._enter_phase(game, nxt, rnd)

    # -- Evidence reveal & events ------------------------------------------

    async def reveal_evidence(self, game: Game, player: GamePlayer, evidence_id: int) -> None:
        if game.current_phase != GamePhase.EVIDENCE:
            raise EngineError("evidence can only be revealed during the evidence phase")
        ev = await self.session.get(Evidence, evidence_id)
        if ev is None or ev.role_id != player.role_id:
            raise EngineError("that evidence is not yours to reveal")

        all_ev = await self._evidence_defs(game.scenario_id)
        unlocked = set(await get_state(game.id, "unlocked_evidence") or [])
        board = list(await get_state(game.id, "board_evidence") or [])
        revealed_ids = set(player.revealed_evidence or [])

        candidate = next((e for e in all_ev if e.id == evidence_id), None)
        if candidate is None or not evidence_dealer.is_revealable(
            candidate,
            current_round=game.current_round,
            unlocked_ids=unlocked,
            already_revealed_ids=revealed_ids,
        ):
            raise EngineError("that evidence is not revealable right now")

        player.revealed_evidence = sorted(revealed_ids | {evidence_id})
        if evidence_id not in board:
            board.append(evidence_id)
        await set_state(game.id, "board_evidence", board)
        await self._log(
            game, player.id, "evidence_revealed", {"evidence_id": evidence_id}
        )
        await publish_event(
            game.id,
            {
                "type": "evidence_revealed",
                "by_player_id": player.id,
                "evidence": self.public_evidence(ev),
            },
        )
        # Reveal may satisfy EVIDENCE_REVEALED / EVIDENCE_COMBINED triggers.
        await self._process_events(
            game, EventContext(revealed_evidence_ids=set(board))
        )

    async def _process_events(self, game: Game, ctx: EventContext) -> None:
        events = await self._event_defs(game.scenario_id)
        fired = set(await get_state(game.id, "fired_events") or [])
        effects = evaluate_events(events, ctx, fired_event_ids=fired)
        if not effects:
            return

        unlocked = set(await get_state(game.id, "unlocked_evidence") or [])
        for eff in effects:
            fired.add(eff.event_id)
            if eff.unlocked_evidence_ids:
                unlocked |= set(eff.unlocked_evidence_ids)
            new_deadline = None
            if eff.seconds_delta:
                new_deadline = await phase_timer.extend(game.id, eff.seconds_delta)
                if new_deadline is not None:
                    game.phase_deadline = datetime.fromtimestamp(new_deadline, tz=UTC)
            await self._log(
                game,
                None,
                "event_fired",
                {"event_id": eff.event_id, "effect": eff.effect_type.value},
            )
            await publish_event(
                game.id,
                {
                    "type": "event_fired",
                    "event_id": eff.event_id,
                    "effect_type": eff.effect_type.value,
                    "narration": eff.narration_text,
                    "unlocked_evidence_ids": list(eff.unlocked_evidence_ids),
                    "new_deadline": new_deadline,
                },
            )
        await set_state(game.id, "unlocked_evidence", sorted(unlocked))
        await set_state(game.id, "fired_events", sorted(fired))

    # -- Voting -------------------------------------------------------------

    async def cast_vote(self, game: Game, player: GamePlayer, location_id: int) -> None:
        if game.current_phase != GamePhase.VOTE:
            raise EngineError("voting is not open")
        player.voted_location_id = location_id
        await self._log(game, player.id, "vote_cast", {"location_id": location_id})
        players = await self._players(game)
        tally = Counter(p.voted_location_id for p in players if p.voted_location_id)
        await publish_event(
            game.id, {"type": "vote_update", "tally": dict(tally)}
        )

    async def guess_insider(self, game: Game, player: GamePlayer, target_player_id: int) -> None:
        if game.current_phase != GamePhase.INSIDER_GUESS:
            raise EngineError("insider guessing is not open")
        player.guessed_insider_player_id = target_player_id
        await self._log(game, player.id, "insider_guess", {})
        # Broadcast only the count of submitted guesses (never the targets).
        players = await self._players(game)
        submitted = sum(1 for p in players if p.guessed_insider_player_id)
        await publish_event(
            game.id, {"type": "insider_guess_update", "submitted": submitted}
        )

    # -- Finalize -----------------------------------------------------------

    async def finalize(self, game: Game) -> None:
        if game.status == GameStatus.FINISHED:
            return
        scenario = await self.session.get(Scenario, game.scenario_id)
        players = await self._players(game)

        if game.chosen_location_id is None:
            tally = Counter(p.voted_location_id for p in players if p.voted_location_id)
            if tally:
                game.chosen_location_id = tally.most_common(1)[0][0]

        all_ev = {e.id: e for e in await self._evidence_defs(game.scenario_id)}
        revealed_by_player = {
            p.id: [all_ev[eid] for eid in (p.revealed_evidence or []) if eid in all_ev]
            for p in players
        }
        result = scoring.compute_scores(
            player_ids=[p.id for p in players],
            insider_player_id=game.insider_player_id,
            chosen_location_id=game.chosen_location_id,
            correct_location_id=scenario.correct_location_id if scenario else None,
            revealed_by_player=revealed_by_player,
            insider_guesses={p.id: p.guessed_insider_player_id for p in players},
        )
        score_by_id = {s.player_id: s for s in result.scores}
        for p in players:
            p.score = score_by_id[p.id].total

        game.outcome = result.outcome
        game.insider_caught = result.insider_caught
        game.current_phase = GamePhase.RESULT
        game.status = GameStatus.FINISHED
        game.phase_deadline = None
        phase_timer.cancel(game.id)

        await self._log(
            game,
            None,
            "game_finished",
            {"outcome": result.outcome.value, "insider_caught": result.insider_caught},
        )
        await publish_event(
            game.id,
            {
                "type": "game_result",
                "outcome": result.outcome.value,
                "insider_caught": result.insider_caught,
                "insider_player_id": game.insider_player_id,
                "correct_location_id": scenario.correct_location_id if scenario else None,
                "truth_story": scenario.truth_story if scenario else "",
                "scores": [
                    {
                        "player_id": s.player_id,
                        "total": s.total,
                        "base": s.base,
                        "contribution": s.contribution,
                        "bonus": s.bonus,
                    }
                    for s in result.scores
                ],
            },
        )

    async def result_payload(self, game: Game) -> dict:
        """Reconstruct the end-game result from persisted state (reconnect-safe)."""
        scenario = await self.session.get(Scenario, game.scenario_id)
        players = await self._players(game)
        return {
            "type": "game_result",
            "outcome": game.outcome.value if game.outcome else None,
            "insider_caught": game.insider_caught,
            "insider_player_id": game.insider_player_id,
            "correct_location_id": scenario.correct_location_id if scenario else None,
            "truth_story": scenario.truth_story if scenario else "",
            "scores": [{"player_id": p.id, "total": p.score} for p in players],
        }

    # -- Serialization ------------------------------------------------------

    @staticmethod
    def public_evidence(ev: Evidence) -> dict:
        """Board-safe evidence view — omits balance metadata (weight, red herring)."""
        return {
            "id": ev.id,
            "title": ev.title,
            "text": ev.text,
            "type": ev.type.value,
            "image": ev.image,
            "location_id": ev.location_id,
        }

    async def public_state(self, game: Game) -> dict:
        """Room state safe to send to everyone (no roles, no private cards)."""
        players = await self._players(game)
        scenario = await self.session.get(Scenario, game.scenario_id)
        location_rows = list(
            await self.session.scalars(
                select(Location).where(Location.scenario_id == game.scenario_id).order_by(Location.id)
            )
        )
        board_ids = await get_state(game.id, "board_evidence") or []
        board_rows = (
            list(
                await self.session.scalars(
                    select(Evidence).where(Evidence.id.in_(board_ids))
                )
            )
            if board_ids
            else []
        )
        tally = Counter(p.voted_location_id for p in players if p.voted_location_id)
        return {
            "id": game.id,
            "code": game.code,
            "status": game.status.value,
            "phase": game.current_phase.value,
            "round": game.current_round,
            "deadline": await get_state(game.id, "phase_deadline"),
            "scenario_id": game.scenario_id,
            "scenario": {
                "title": scenario.title if scenario else "",
                "intro_text": scenario.intro_text if scenario else "",
                "task_text": scenario.task_text if scenario else "",
                "map_image": scenario.map_image if scenario else None,
                "cover_image": scenario.cover_image if scenario else None,
                "rounds": self._rounds(game, scenario) if scenario else 1,
            },
            # Locations are public map knowledge; the correct-answer flag is NOT sent.
            "locations": [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "description": loc.description,
                    "map_x": loc.map_x,
                    "map_y": loc.map_y,
                    "image": loc.image,
                }
                for loc in location_rows
            ],
            "players": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "is_host": p.is_host,
                    "connected": p.connected,
                    "score": p.score,
                }
                for p in players
            ],
            "board": [self.public_evidence(e) for e in board_rows],
            "vote_tally": dict(tally),
        }

    async def player_snapshot(self, game: Game, player: GamePlayer) -> dict:
        """Everything one player may see, including their secrets. Never broadcast."""
        state = await self.public_state(game)
        role = await self.session.get(Role, player.role_id) if player.role_id else None
        all_ev = await self._evidence_defs(game.scenario_id)
        unlocked = set(await get_state(game.id, "unlocked_evidence") or [])
        revealed_ids = set(player.revealed_evidence or [])

        owned_ids = [e.id for e in evidence_dealer.owned_evidence(all_ev, player.role_id or -1)]
        owned_rows = (
            list(
                await self.session.scalars(
                    select(Evidence).where(Evidence.id.in_(owned_ids))
                )
            )
            if owned_ids
            else []
        )
        revealable = {
            e.id
            for e in evidence_dealer.revealable_evidence(
                all_ev,
                player.role_id or -1,
                current_round=game.current_round,
                unlocked_ids=unlocked,
                already_revealed_ids=revealed_ids,
            )
        }

        insider_goal = None
        if player.is_insider:
            scenario = await self.session.get(Scenario, game.scenario_id)
            target = scenario.correct_answer_text if scenario else "the truth"
            insider_goal = (
                "You are the INSIDER. Your evidence is genuine, but you must steer the "
                f"team away from {target}. Make them choose wrong — or run out the clock."
            )

        state["me"] = {
            "player_id": player.id,
            "is_host": player.is_host,
            "is_insider": player.is_insider,
            "insider_goal": insider_goal,
            "role": (
                {"id": role.id, "name": role.name, "description": role.description, "icon": role.icon}
                if role
                else None
            ),
            "hand": [
                {
                    **self.public_evidence(e),
                    "revealed": e.id in revealed_ids,
                    "revealable": e.id in revealable,
                    "reveal_phase": e.reveal_phase,
                }
                for e in owned_rows
            ],
        }
        return state

    # -- Logging ------------------------------------------------------------

    async def _log(self, game: Game, actor_player_id: int | None, action: str, payload: dict) -> None:
        self.session.add(
            GameLog(
                game_id=game.id,
                actor_player_id=actor_player_id,
                action=action,
                payload=payload,
                phase=game.current_phase.value,
                round=game.current_round,
            )
        )


async def on_phase_timeout(game_id: int) -> None:
    """Timer callback: auto-advance a game whose phase deadline elapsed.

    Runs outside any request, so it opens its own transactional session.
    """
    from app.core.database import session_scope

    async with session_scope() as session:
        engine = GameEngine(session)
        game = await engine.get_game(game_id)
        if game and game.status == GameStatus.IN_PROGRESS:
            await engine.advance_phase(game, reason="timeout")
