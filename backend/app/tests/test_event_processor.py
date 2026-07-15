from app.core.enums import EffectType, TriggerType
from app.services.game_engine import event_processor as ep
from app.services.game_engine.types import EventDef


def _combined_event():
    return EventDef(
        id=1,
        trigger_type=TriggerType.EVIDENCE_COMBINED,
        trigger_payload={"evidence_ids": [5, 3]},
        effect_type=EffectType.UNLOCK_EVIDENCE,
        effect_payload={"evidence_ids": [11]},
        narration_text="unlocked!",
        fire_once=True,
    )


def test_combined_requires_all_evidence():
    event = _combined_event()
    # Only one of the two present -> no fire.
    ctx = ep.EventContext(revealed_evidence_ids={5})
    assert ep.evaluate_events([event], ctx) == []
    # Both present -> fires and unlocks id 11.
    ctx = ep.EventContext(revealed_evidence_ids={5, 3})
    effects = ep.evaluate_events([event], ctx)
    assert len(effects) == 1
    assert effects[0].unlocked_evidence_ids == (11,)


def test_revealed_fires_on_any():
    event = EventDef(
        id=2,
        trigger_type=TriggerType.EVIDENCE_REVEALED,
        trigger_payload={"evidence_ids": [7, 8]},
        effect_type=EffectType.REVEAL_HINT,
        effect_payload={"text": "hint"},
    )
    ctx = ep.EventContext(revealed_evidence_ids={8})
    assert len(ep.evaluate_events([event], ctx)) == 1


def test_fire_once_respected():
    event = _combined_event()
    ctx = ep.EventContext(revealed_evidence_ids={5, 3})
    assert ep.evaluate_events([event], ctx, fired_event_ids={1}) == []


def test_add_and_remove_time_sign():
    add = EventDef(
        id=3,
        trigger_type=TriggerType.PHASE_STARTED,
        trigger_payload={"phase": "vote"},
        effect_type=EffectType.ADD_TIME,
        effect_payload={"seconds": 30},
    )
    remove = EventDef(
        id=4,
        trigger_type=TriggerType.PHASE_STARTED,
        trigger_payload={"phase": "vote"},
        effect_type=EffectType.REMOVE_TIME,
        effect_payload={"seconds": 30},
    )
    ctx = ep.EventContext(phase="vote")
    effects = {e.event_id: e for e in ep.evaluate_events([add, remove], ctx)}
    assert effects[3].seconds_delta == 30
    assert effects[4].seconds_delta == -30


def test_phase_started_no_match():
    event = EventDef(
        id=5,
        trigger_type=TriggerType.PHASE_STARTED,
        trigger_payload={"phase": "vote"},
        effect_type=EffectType.REVEAL_HINT,
        effect_payload={},
    )
    ctx = ep.EventContext(phase="discussion")
    assert ep.evaluate_events([event], ctx) == []
