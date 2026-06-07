"""Central router registration."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.emotion import router as emotion_router
from app.api.report import router as report_router
from app.api.trend import router as trend_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(emotion_router)
api_router.include_router(report_router)
api_router.include_router(trend_router)
