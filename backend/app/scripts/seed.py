"""Seed the demo content: an Ecology genre + the full "City Pollution" scenario.

Idempotent: re-running skips creation if the demo scenario already exists.

Run with:  python -m app.scripts.seed
"""
import asyncio

from sqlalchemy import select

from app.core.database import session_scope
from app.core.enums import EffectType, EvidenceType, TriggerType, UserRole
from app.core.security import hash_password
from app.models import (
    Evidence,
    Event,
    Genre,
    Location,
    Role,
    Scenario,
    User,
)

DEMO_TITLE = "City Pollution"


async def _ensure_admin(session) -> None:
    existing = await session.scalar(select(User).where(User.username == "admin"))
    if existing:
        return
    session.add(
        User(
            username="admin",
            display_name="Game Master",
            hashed_password=hash_password("admin"),
            role=UserRole.ADMIN,
            language="en",
        )
    )


async def _build_city_pollution(session) -> Scenario:
    genre = await session.scalar(select(Genre).where(Genre.name == "Ecology"))
    if genre is None:
        genre = Genre(
            name="Ecology",
            description="Environmental disasters, pollution and cover-ups.",
            icon="leaf",
            color="#22c55e",
        )
        session.add(genre)
        await session.flush()

    scenario = Scenario(
        genre_id=genre.id,
        title=DEMO_TITLE,
        intro_text=(
            "The river that feeds our city has turned a sickly green. Fish float "
            "belly-up, children fall ill, and the air by the waterfront reeks of "
            "chemicals. The Mayor insists it is a 'natural algae bloom.' Nobody "
            "believes that anymore."
        ),
        task_text=(
            "Your duty: find the true source of the poisoning before the city "
            "council buries the case. One of you is not who they claim to be."
        ),
        difficulty=2,
        min_players=3,
        max_players=6,
        rounds=2,
        timers={
            "intro": 60,
            "evidence": 90,
            "discussion": 150,
            "vote": 60,
            "insider_guess": 45,
        },
        truth_story=(
            "The Riverside Textile Factory, fast-tracked through zoning by a bribed "
            "Mayor, built an illegal discharge pipe behind its warehouse. Every "
            "night, trucks hauled away barrels while the pipe bled heavy-metal dye "
            "effluent straight into the river delta. Downstream residents drank and "
            "bathed in it; the hospital filled with heavy-metal poisoning. The "
            "'algae bloom' was a lie to protect the permit — and the Mayor who "
            "signed it."
        ),
        is_published=True,
    )
    session.add(scenario)
    await session.flush()

    # --- Locations (8) -----------------------------------------------------
    loc_specs = [
        ("Riverside Textile Factory", "A sprawling dye works on the north bank.", 72, 28, True),
        ("City Hall", "Seat of the Mayor and the zoning council.", 45, 55, False),
        ("River Delta", "Where the river meets the sea — now green and foul.", 60, 75, False),
        ("Central Hospital", "Overflowing with mysteriously ill patients.", 30, 40, False),
        ("Old Water Treatment Plant", "Decommissioned, blamed by rumor.", 20, 65, False),
        ("Residential District", "Riverside homes drawing from the tainted water.", 50, 82, False),
        ("Farmers Market", "Produce and fish sold to the whole city.", 40, 68, False),
        ("Industrial Docks", "Barrels come and go here after dark.", 82, 48, False),
    ]
    locations: dict[str, Location] = {}
    for name, desc, x, y, correct in loc_specs:
        loc = Location(
            scenario_id=scenario.id,
            name=name,
            description=desc,
            map_x=float(x),
            map_y=float(y),
            is_correct_answer=correct,
        )
        session.add(loc)
        locations[name] = loc
    await session.flush()

    scenario.correct_location_id = locations["Riverside Textile Factory"].id
    scenario.correct_answer_text = "Riverside Textile Factory"

    # --- Roles (5) ---------------------------------------------------------
    role_specs = [
        ("Mayor", "Signed the factory's permit. Charismatic, evasive.", "crown", True),
        ("Doctor", "Runs the hospital ward drowning in sick patients.", "stethoscope", False),
        ("Police Officer", "Patrols the docks; keeps a quiet notebook.", "shield", True),
        ("Concerned Citizen", "Lives by the river and has had enough.", "user", True),
        ("Ill Person", "A factory worker, now bedridden and afraid.", "heart-pulse", False),
    ]
    roles: dict[str, Role] = {}
    for name, desc, icon, insider in role_specs:
        r = Role(
            scenario_id=scenario.id,
            name=name,
            description=desc,
            icon=icon,
            can_be_insider=insider,
        )
        session.add(r)
        roles[name] = r
    await session.flush()

    # --- Evidence (13) -----------------------------------------------------
    # (role, location|None, title, text, type, red_herring, reveal_phase, weight, locked)
    ev_specs = [
        # Mayor
        ("Mayor", "Riverside Textile Factory", "Fast-Tracked Zoning Permit",
         "The factory's permit was approved in three days, skipping the environmental review.",
         EvidenceType.DOCUMENT, False, 1, 3, False),
        ("Mayor", "City Hall", "Council Meeting Minutes",
         "The council spent hours debating noise at the Industrial Docks.",
         EvidenceType.DOCUMENT, True, 2, 1, False),
        ("Mayor", "City Hall", "Offshore Bank Transfer",
         "A wire of 200,000 from a shell company tied to the factory's owner.",
         EvidenceType.DOCUMENT, False, 3, 3, True),
        # Doctor
        ("Doctor", "Central Hospital", "Chemical Poisoning Report",
         "Bloodwork shows heavy-metal toxicity — cadmium and chromium, not infection.",
         EvidenceType.MEDICAL, False, 1, 3, False),
        ("Doctor", "Residential District", "Patient Cluster Map",
         "Every case lives downstream of the north bank, along the delta.",
         EvidenceType.MEDICAL, False, 2, 2, False),
        ("Doctor", "River Delta", "Water Sample Analysis",
         "Lab confirms textile dye compounds and chromium far above safe limits.",
         EvidenceType.PHYSICAL, False, 3, 4, True),
        # Police
        ("Police Officer", "Industrial Docks", "Night Truck Log",
         "Unmarked trucks leave the factory between 2 and 4 AM, five nights a week.",
         EvidenceType.DOCUMENT, False, 1, 2, False),
        ("Police Officer", "Old Water Treatment Plant", "Anonymous Tip",
         "A caller swears the old treatment plant is leaking. (The plant is dry.)",
         EvidenceType.RUMOR, True, 2, 1, False),
        ("Police Officer", "Riverside Textile Factory", "Hidden Discharge Pipe Photo",
         "A whistleblower's photo: a concealed pipe behind the factory, gushing green.",
         EvidenceType.PHYSICAL, False, 3, 5, True),
        # Citizen
        ("Concerned Citizen", "River Delta", "Foul Smell Complaint",
         "A logged complaint of a burning-chemical stench near the north bank.",
         EvidenceType.WITNESS, False, 1, 2, False),
        ("Concerned Citizen", "River Delta", "Dead Fish Photograph",
         "Hundreds of fish dead along the bank nearest the factory outflow.",
         EvidenceType.PHYSICAL, False, 2, 2, False),
        # Ill Person
        ("Ill Person", "Central Hospital", "Symptom Diary",
         "Numb hands, metallic taste, failing kidneys — textbook heavy-metal poisoning.",
         EvidenceType.MEDICAL, False, 1, 2, False),
        ("Ill Person", "Riverside Textile Factory", "Factory Floor Testimony",
         "I worked the dye vats. At night the foreman drained them 'out back.'",
         EvidenceType.WITNESS, False, 2, 3, False),
    ]
    evidence: dict[str, Evidence] = {}
    for role_name, loc_name, title, text, etype, rh, phase, weight, locked in ev_specs:
        ev = Evidence(
            scenario_id=scenario.id,
            role_id=roles[role_name].id,
            location_id=locations[loc_name].id if loc_name else None,
            title=title,
            text=text,
            type=etype,
            is_red_herring=rh,
            reveal_phase=phase,
            weight=weight,
            starts_locked=locked,
        )
        session.add(ev)
        evidence[title] = ev
    await session.flush()

    # --- Events (3 conditional) -------------------------------------------
    events = [
        Event(
            scenario_id=scenario.id,
            name="Whistleblower Photo",
            trigger_type=TriggerType.EVIDENCE_COMBINED,
            trigger_payload={
                "evidence_ids": [
                    evidence["Night Truck Log"].id,
                    evidence["Chemical Poisoning Report"].id,
                ]
            },
            effect_type=EffectType.UNLOCK_EVIDENCE,
            effect_payload={"evidence_ids": [evidence["Hidden Discharge Pipe Photo"].id]},
            narration_text=(
                "Your phone buzzes. An anonymous number sends a single photo — a "
                "hidden pipe behind the textile factory, bleeding green into the dark."
            ),
            fire_once=True,
        ),
        Event(
            scenario_id=scenario.id,
            name="NGO Rushes the Lab",
            trigger_type=TriggerType.EVIDENCE_COMBINED,
            trigger_payload={
                "evidence_ids": [
                    evidence["Foul Smell Complaint"].id,
                    evidence["Dead Fish Photograph"].id,
                ]
            },
            effect_type=EffectType.UNLOCK_EVIDENCE,
            effect_payload={
                "evidence_ids": [evidence["Water Sample Analysis"].id],
                "seconds": 60,
            },
            narration_text=(
                "An environmental NGO hears your case and rushes a river sample to "
                "the lab. The results will change everything. (+60 seconds)"
            ),
            fire_once=True,
        ),
        Event(
            scenario_id=scenario.id,
            name="The Money Trail",
            trigger_type=TriggerType.EVIDENCE_COMBINED,
            trigger_payload={
                "evidence_ids": [
                    evidence["Fast-Tracked Zoning Permit"].id,
                    evidence["Hidden Discharge Pipe Photo"].id,
                ]
            },
            effect_type=EffectType.UNLOCK_EVIDENCE,
            effect_payload={"evidence_ids": [evidence["Offshore Bank Transfer"].id]},
            narration_text=(
                "The permit and the pipe together are damning. A forensic accountant "
                "surfaces a wire transfer — someone at this table was paid to look away."
            ),
            fire_once=True,
        ),
    ]
    session.add_all(events)
    await session.flush()
    return scenario


async def seed() -> None:
    async with session_scope() as session:
        await _ensure_admin(session)
        existing = await session.scalar(
            select(Scenario).where(Scenario.title == DEMO_TITLE)
        )
        if existing:
            print(f"Demo scenario '{DEMO_TITLE}' already present (id={existing.id}); skipping.")
            return
        scenario = await _build_city_pollution(session)
        print(f"Seeded genre 'Ecology' and scenario '{DEMO_TITLE}' (id={scenario.id}).")


if __name__ == "__main__":
    asyncio.run(seed())
