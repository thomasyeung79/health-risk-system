"""Trend analysis API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.trend import MetricTrend, TrendSummaryResponse
from app.services.trend_engine.trend_service import compute_summary

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])


@router.get("/summary", response_model=TrendSummaryResponse)
def get_trend_summary(
    days: int = Query(default=7, ge=1, le=90),
    language: str = Query(default="English"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get trend summary for core metrics over the given window."""
    result = compute_summary(db=db, user_id=current_user.id, days=days, language=language)

    return TrendSummaryResponse(
        days_analyzed=result["days_analyzed"],
        health_data_points=result["health_data_points"],
        emotion_data_points=result["emotion_data_points"],
        overall_direction=result["overall_direction"],
        metrics=[MetricTrend(**m) for m in result["metrics"]],
    )
