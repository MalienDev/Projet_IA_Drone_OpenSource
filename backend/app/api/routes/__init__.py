"""
API routes.
"""

from fastapi import APIRouter
from . import health, drones, zones, events, auth

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(drones.router, prefix="/drones", tags=["drones"])
api_router.include_router(zones.router, prefix="/zones", tags=["zones"])
api_router.include_router(events.router, prefix="/events", tags=["events"])

__all__ = ["api_router"]
