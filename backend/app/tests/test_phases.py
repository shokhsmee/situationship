from app.core.enums import GamePhase
from app.services.game_engine import phases


def _run_to_end(total_rounds: int, insider_enabled: bool) -> list[tuple[GamePhase, int]]:
    seq: list[tuple[GamePhase, int]] = []
    phase, rnd = GamePhase.LOBBY, 0
    for _ in range(50):  # safety bound
        phase, rnd = phases.advance(phase, rnd, total_rounds, insider_enabled=insider_enabled)
        seq.append((phase, rnd))
        if phases.is_terminal(phase):
            break
    return seq


def test_two_round_flow_with_insider():
    seq = _run_to_end(total_rounds=2, insider_enabled=True)
    assert seq == [
        (GamePhase.INTRO, 0),
        (GamePhase.EVIDENCE, 1),
        (GamePhase.DISCUSSION, 1),
        (GamePhase.EVIDENCE, 2),
        (GamePhase.DISCUSSION, 2),
        (GamePhase.VOTE, 2),
        (GamePhase.INSIDER_GUESS, 2),
        (GamePhase.RESULT, 2),
    ]


def test_insider_disabled_skips_guess_phase():
    seq = _run_to_end(total_rounds=1, insider_enabled=False)
    assert (GamePhase.INSIDER_GUESS, 1) not in seq
    assert seq[-1] == (GamePhase.RESULT, 1)
    # Single round: one evidence/discussion pair then straight to vote.
    assert seq == [
        (GamePhase.INTRO, 0),
        (GamePhase.EVIDENCE, 1),
        (GamePhase.DISCUSSION, 1),
        (GamePhase.VOTE, 1),
        (GamePhase.RESULT, 1),
    ]


def test_result_is_terminal():
    assert phases.is_terminal(GamePhase.RESULT)
    assert phases.advance(GamePhase.RESULT, 2, 2) == (GamePhase.RESULT, 2)


def test_initial_phase():
    assert phases.initial_phase() == (GamePhase.INTRO, 0)
