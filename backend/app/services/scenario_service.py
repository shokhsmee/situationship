"""Scenario authoring helpers: detail assembly + publish-time validation."""
from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Evidence, Event, Location, Role, Scenario
from app.schemas.scenario import ScenarioValidation

MIN_EVIDENCE_PER_ROLE = 2


async def load_detail(session: AsyncSession, scenario_id: int) -> Scenario | None:
    return await session.scalar(
        select(Scenario)
        .where(Scenario.id == scenario_id)
        .options(
            selectinload(Scenario.locations),
            selectinload(Scenario.roles),
            selectinload(Scenario.evidence),
            selectinload(Scenario.events),
        )
    )


async def validate_scenario(session: AsyncSession, scenario_id: int) -> ScenarioValidation:
    """Run the publish checklist from the spec. Returns errors + warnings."""
    scenario = await load_detail(session, scenario_id)
    if scenario is None:
        return ScenarioValidation(valid=False, errors=["scenario not found"])

    errors: list[str] = []
    warnings: list[str] = []

    roles = scenario.roles
    evidence = scenario.evidence
    locations = scenario.locations

    if not roles:
        errors.append("scenario has no roles")
    if not locations:
        errors.append("scenario has no locations")

    # Correct answer must exist.
    correct_loc = next((loc for loc in locations if loc.is_correct_answer), None)
    if scenario.correct_location_id is None and not scenario.correct_answer_text:
        errors.append("no correct answer set")
    if correct_loc is None and scenario.correct_location_id is None:
        warnings.append("no location is flagged as the correct answer")

    # Every role needs at least MIN_EVIDENCE_PER_ROLE evidence.
    per_role = Counter(e.role_id for e in evidence)
    for role in roles:
        if per_role.get(role.id, 0) < MIN_EVIDENCE_PER_ROLE:
            errors.append(
                f"role '{role.name}' has fewer than {MIN_EVIDENCE_PER_ROLE} evidence items"
            )

    # At least one insider-capable role.
    if roles and not any(r.can_be_insider for r in roles):
        errors.append("no role is allowed to be the insider")

    # Reachability: the correct location should have at least one genuine clue.
    if scenario.correct_location_id is not None:
        genuine_at_correct = [
            e
            for e in evidence
            if e.location_id == scenario.correct_location_id and not e.is_red_herring
        ]
        if not genuine_at_correct:
            warnings.append("no genuine evidence points at the correct location")

    # No orphan events (payloads referencing missing evidence ids).
    evidence_ids = {e.id for e in evidence}
    for event in scenario.events:
        referenced = set(event.trigger_payload.get("evidence_ids", [])) | set(
            event.effect_payload.get("evidence_ids", [])
        )
        missing = referenced - evidence_ids
        if missing:
            errors.append(f"event '{event.name or event.id}' references missing evidence {sorted(missing)}")

    if not scenario.truth_story:
        warnings.append("truth story is empty")
    if not scenario.events:
        warnings.append("scenario has no conditional events")
    if roles and scenario.min_players > len(roles):
        warnings.append("min_players exceeds the number of roles")

    return ScenarioValidation(valid=not errors, errors=errors, warnings=warnings)
