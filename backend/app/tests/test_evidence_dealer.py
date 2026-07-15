from app.services.game_engine import evidence_dealer as dealer
from app.services.game_engine.types import EvidenceDef


def _ev(id, role_id, phase=1, locked=False, weight=1, rh=False):
    return EvidenceDef(
        id=id,
        role_id=role_id,
        reveal_phase=phase,
        starts_locked=locked,
        weight=weight,
        is_red_herring=rh,
    )


EVIDENCE = [
    _ev(1, role_id=1, phase=1),
    _ev(2, role_id=1, phase=2),
    _ev(3, role_id=1, phase=3, locked=True),  # unlocked only by event
    _ev(4, role_id=2, phase=1),
]


def test_owned_filters_by_role_and_sorts():
    owned = dealer.owned_evidence(EVIDENCE, role_id=1)
    assert [e.id for e in owned] == [1, 2, 3]


def test_round_gates_reveal_phase():
    r1 = dealer.revealable_evidence(EVIDENCE, role_id=1, current_round=1)
    assert [e.id for e in r1] == [1]
    r2 = dealer.revealable_evidence(EVIDENCE, role_id=1, current_round=2)
    assert [e.id for e in r2] == [1, 2]


def test_locked_evidence_hidden_until_unlocked():
    # Round 3 reached but card 3 still locked.
    r3 = dealer.revealable_evidence(EVIDENCE, role_id=1, current_round=3)
    assert 3 not in [e.id for e in r3]
    # Once unlocked it appears.
    r3u = dealer.revealable_evidence(
        EVIDENCE, role_id=1, current_round=3, unlocked_ids={3}
    )
    assert 3 in [e.id for e in r3u]


def test_already_revealed_excluded():
    r = dealer.revealable_evidence(
        EVIDENCE, role_id=1, current_round=2, already_revealed_ids={1}
    )
    assert [e.id for e in r] == [2]
