import random

from app.services.game_engine.role_assigner import assign_roles
from app.services.game_engine.types import RoleDef

ROLES = [
    RoleDef(id=1, name="Mayor", can_be_insider=True),
    RoleDef(id=2, name="Doctor", can_be_insider=False),
    RoleDef(id=3, name="Police", can_be_insider=True),
    RoleDef(id=4, name="Citizen", can_be_insider=True),
    RoleDef(id=5, name="Ill", can_be_insider=False),
]


def test_every_player_gets_exactly_one_role():
    result = assign_roles([10, 11, 12], ROLES, rng=random.Random(1))
    assert {a.player_id for a in result} == {10, 11, 12}
    assert len(result) == 3


def test_exactly_one_insider_when_enabled():
    result = assign_roles([10, 11, 12, 13], ROLES, insider_enabled=True, rng=random.Random(2))
    insiders = [a for a in result if a.is_insider]
    assert len(insiders) == 1
    # Insider must hold an insider-capable role.
    insider_role = next(r for r in ROLES if r.id == insiders[0].role_id)
    assert insider_role.can_be_insider


def test_no_insider_when_disabled():
    result = assign_roles([10, 11, 12], ROLES, insider_enabled=False, rng=random.Random(3))
    assert not any(a.is_insider for a in result)


def test_no_insider_when_no_eligible_role():
    non_insider_roles = [r for r in ROLES if not r.can_be_insider]
    result = assign_roles([10, 11], non_insider_roles, insider_enabled=True, rng=random.Random(4))
    assert not any(a.is_insider for a in result)


def test_deterministic_under_seed():
    a = assign_roles([1, 2, 3], ROLES, rng=random.Random(42))
    b = assign_roles([1, 2, 3], ROLES, rng=random.Random(42))
    assert a == b


def test_more_players_than_roles_cycles():
    two_roles = ROLES[:2]
    result = assign_roles([1, 2, 3, 4, 5], two_roles, insider_enabled=False, rng=random.Random(5))
    assert len(result) == 5
    assert all(a.role_id in {1, 2} for a in result)
