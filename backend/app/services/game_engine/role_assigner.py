"""Random role assignment + insider selection (pure).

An injectable `random.Random` keeps assignment deterministic under test.
"""
from __future__ import annotations

import random

from app.services.game_engine.types import RoleAssignment, RoleDef


def assign_roles(
    player_ids: list[int],
    roles: list[RoleDef],
    *,
    insider_enabled: bool = True,
    rng: random.Random | None = None,
) -> list[RoleAssignment]:
    """Deal one role per player and (optionally) pick a single insider.

    If there are more players than distinct roles, roles are reused cyclically.
    The insider is chosen only among players whose role `can_be_insider`.
    """
    if not player_ids:
        return []
    if not roles:
        raise ValueError("cannot assign roles: scenario has no roles")

    rng = rng or random.Random()

    shuffled_roles = roles[:]
    rng.shuffle(shuffled_roles)
    shuffled_players = player_ids[:]
    rng.shuffle(shuffled_players)

    assignments: list[RoleAssignment] = []
    for idx, player_id in enumerate(shuffled_players):
        role = shuffled_roles[idx % len(shuffled_roles)]
        assignments.append(
            RoleAssignment(player_id=player_id, role_id=role.id, is_insider=False)
        )

    if not insider_enabled:
        return assignments

    role_by_id = {r.id: r for r in roles}
    eligible = [a for a in assignments if role_by_id[a.role_id].can_be_insider]
    if not eligible:
        return assignments

    chosen = rng.choice(eligible)
    return [
        RoleAssignment(a.player_id, a.role_id, is_insider=(a is chosen))
        for a in assignments
    ]
