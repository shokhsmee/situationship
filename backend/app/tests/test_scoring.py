from app.core.enums import GameOutcome
from app.services.game_engine import scoring
from app.services.game_engine.types import EvidenceDef


def _ev(id, weight=1, rh=False):
    return EvidenceDef(
        id=id, role_id=1, reveal_phase=1, starts_locked=False, weight=weight, is_red_herring=rh
    )


def test_investigators_win_awards_base_to_investigators():
    result = scoring.compute_scores(
        player_ids=[1, 2, 3],
        insider_player_id=3,
        chosen_location_id=99,
        correct_location_id=99,
        revealed_by_player={},
    )
    assert result.outcome == GameOutcome.INVESTIGATORS_WIN
    by_id = {s.player_id: s for s in result.scores}
    assert by_id[1].base == scoring.WIN_BASE
    assert by_id[2].base == scoring.WIN_BASE
    assert by_id[3].base == 0  # insider gets no base when team wins


def test_wrong_answer_is_insider_win():
    result = scoring.compute_scores(
        player_ids=[1, 2, 3],
        insider_player_id=3,
        chosen_location_id=1,
        correct_location_id=99,
        revealed_by_player={},
    )
    assert result.outcome == GameOutcome.INSIDER_WIN
    assert {s.player_id: s.base for s in result.scores}[3] == scoring.INSIDER_WIN_BASE


def test_timeout_no_answer_is_insider_win():
    result = scoring.compute_scores(
        player_ids=[1, 2],
        insider_player_id=2,
        chosen_location_id=None,
        correct_location_id=99,
        revealed_by_player={},
    )
    assert result.outcome == GameOutcome.INSIDER_WIN


def test_contribution_excludes_red_herrings():
    result = scoring.compute_scores(
        player_ids=[1],
        insider_player_id=None,
        chosen_location_id=99,
        correct_location_id=99,
        revealed_by_player={1: [_ev(1, weight=3), _ev(2, weight=5, rh=True)]},
    )
    ps = result.scores[0]
    # Only the weight-3 genuine card counts.
    assert ps.contribution == 3 * scoring.CONTRIBUTION_PER_WEIGHT


def test_insider_caught_by_majority():
    # Players 1,2 (investigators) both point at 3 (insider); 3 votes noise.
    result = scoring.compute_scores(
        player_ids=[1, 2, 3],
        insider_player_id=3,
        chosen_location_id=1,
        correct_location_id=99,
        revealed_by_player={},
        insider_guesses={1: 3, 2: 3, 3: 1},
    )
    assert result.insider_caught is True
    by_id = {s.player_id: s for s in result.scores}
    assert by_id[1].bonus == scoring.CATCH_INSIDER_BONUS
    assert by_id[3].bonus == -scoring.INSIDER_CAUGHT_PENALTY


def test_insider_not_caught_without_majority():
    result = scoring.compute_scores(
        player_ids=[1, 2, 3],
        insider_player_id=3,
        chosen_location_id=1,
        correct_location_id=99,
        revealed_by_player={},
        insider_guesses={1: 3, 2: 1, 3: 1},  # tie, no strict majority
    )
    assert result.insider_caught is False


def test_total_property_sums_components():
    result = scoring.compute_scores(
        player_ids=[1, 2],
        insider_player_id=2,
        chosen_location_id=99,
        correct_location_id=99,
        revealed_by_player={1: [_ev(1, weight=2)]},
        insider_guesses={1: 2},  # single voter, majority -> caught
    )
    ps = {s.player_id: s for s in result.scores}[1]
    assert ps.total == ps.base + ps.contribution + ps.bonus
    assert ps.total == scoring.WIN_BASE + 2 * scoring.CONTRIBUTION_PER_WEIGHT + scoring.CATCH_INSIDER_BONUS
