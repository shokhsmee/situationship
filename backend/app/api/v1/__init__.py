"""Aggregate all v1 routers behind a single APIRouter.

Sub-routers are attached in the game-API stage; kept here so main.py depends on
exactly one import.
"""
from fastapi import APIRouter

from app.api.v1 import (
    admin_evidence,
    admin_events,
    admin_genres,
    admin_locations,
    admin_roles,
    admin_scenarios,
    auth,
    games,
    gameplay,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(gameplay.router, prefix="/games", tags=["gameplay"])
api_router.include_router(admin_genres.router, prefix="/admin/genres", tags=["admin:genres"])
api_router.include_router(
    admin_scenarios.router, prefix="/admin/scenarios", tags=["admin:scenarios"]
)
api_router.include_router(
    admin_locations.router, prefix="/admin/locations", tags=["admin:locations"]
)
api_router.include_router(admin_roles.router, prefix="/admin/roles", tags=["admin:roles"])
api_router.include_router(
    admin_evidence.router, prefix="/admin/evidence", tags=["admin:evidence"]
)
api_router.include_router(admin_events.router, prefix="/admin/events", tags=["admin:events"])
