"""End-game scoring and outcome resolution (pure)."""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from app.core.enums import GameOutcome
from app.services.game_engine.types import EvidenceDef, PlayerScore, ScoreResult

# Tunable scoring constants.
WIN_BASE = 100
INSIDER_WIN_BASE = 150
CONTRIBUTION_PER_WEIGHT = 5
CATCH_INSIDER_BONUS = 50
INSIDER_CAUGHT_PENALTY = 50


def resolve_outcome(
    chosen_location_id: int | None,
    correct_location_id: int | None,
) -> GameOutcome:
    if chosen_location_id is None:
        return GameOutcome.INSIDER_WIN  # timeout / no answer
    if correct_location_id is not None and chosen_location_id == correct_location_id:
        return GameOutcome.INVESTIGATORS_WIN
    return GameOutcome.INSIDER_WIN


def _insider_caught(
    insider_player_id: int | None,
    guesses: dict[int, int | None],
) -> bool:
    """True if a strict majority of non-insider guessers named the real insider."""
    if insider_player_id is None:
        return False
    voters = {
        pid: guess
        for pid, guess in guesses.items()
        if pid != insider_player_id and guess is not None
    }
    if not voters:
        return False
    tally = Counter(voters.values())
    top_target, top_votes = tally.most_common(1)[0]
    return top_target == insider_player_id and top_votes * 2 > len(voters)


def compute_scores(
    *,
    player_ids: list[int],
    insider_player_id: int | None,
    chosen_location_id: int | None,
    correct_location_id: int | None,
    revealed_by_player: dict[int, list[EvidenceDef]],
    insider_guesses: dict[int, int | None] | None = None,
) -> ScoreResult:
    """Compute every player's score plus the game outcome.

    Investigators win => base to investigators. Insider wins => base to insider.
    Contribution rewards revealing genuine (non-red-herring) evidence.
    Catching the insider grants investigators a bonus and penalises the insider.
    """
    insider_guesses = insider_guesses or {}
    outcome = resolve_outcome(chosen_location_id, correct_location_id)
    caught = _insider_caught(insider_player_id, insider_guesses)
    investigators_won = outcome == GameOutcome.INVESTIGATORS_WIN

    scores: list[PlayerScore] = []
    for pid in player_ids:
        is_insider = pid == insider_player_id
        ps = PlayerScore(player_id=pid, is_insider=is_insider)

        # Base — awarded to the winning side.
        if is_insider and not investigators_won:
            ps.base = INSIDER_WIN_BASE
        elif not is_insider and investigators_won:
            ps.base = WIN_BASE

        # Contribution — genuine evidence brought to the board.
        genuine = [e for e in revealed_by_player.get(pid, []) if not e.is_red_herring]
        ps.contribution = sum(e.weight for e in genuine) * CONTRIBUTION_PER_WEIGHT

        # Insider-catch bonus / penalty.
        if caught:
            if is_insider:
                ps.bonus -= INSIDER_CAUGHT_PENALTY
            else:
                ps.bonus += CATCH_INSIDER_BONUS

        scores.append(ps)

    return ScoreResult(outcome=outcome, insider_caught=caught, scores=scores)
