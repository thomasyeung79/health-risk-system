"""Central router registration."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.emotion import router as emotion_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(emotion_router)
