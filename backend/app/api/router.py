"""Central router registration."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.emotion import router as emotion_router
from app.api.report import router as report_router
from app.api.trend import router as trend_router
from app.api.members import router as members_router
from app.api.consultations import router as consultations_router
from app.api.ai_reports import router as ai_reports_router
from app.api.healing_plans import router as healing_plans_router
from app.api.community_cases import router as community_cases_router
from app.api.dashboard import router as dashboard_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(emotion_router)
api_router.include_router(report_router)
api_router.include_router(trend_router)
api_router.include_router(members_router)
api_router.include_router(consultations_router)
api_router.include_router(ai_reports_router)
api_router.include_router(healing_plans_router)
api_router.include_router(community_cases_router)
api_router.include_router(dashboard_router)
