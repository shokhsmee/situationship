"""Game engine: a phase state machine plus pure rule modules.

Design: the rule modules (phases, role_assigner, evidence_dealer,
event_processor, scoring) are PURE and operate on the lightweight dataclasses in
`types.py` — no DB, no Redis, no clock — so they are trivially unit-testable.
`engine.py` is the only module that performs IO, mapping ORM rows into these
dataclasses and persisting results.
"""
