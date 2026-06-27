"""Dashboard API route — aggregated summary of wellness OS metrics."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_report import AIReport
from app.models.community_case import CommunityCase
from app.models.consultation import Consultation
from app.models.healing_plan import HealingPlan
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import ConsultationResponse, DashboardSummaryResponse, MemberResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = current_user.id
    tm = db.query(Member).filter(Member.user_id == uid).count()
    tc = db.query(Consultation).filter(Consultation.user_id == uid).count()
    ta = db.query(AIReport).filter(AIReport.user_id == uid).count()
    th = db.query(HealingPlan).filter(HealingPlan.user_id == uid).count()
    tcc = db.query(CommunityCase).filter(
        (CommunityCase.is_public == True) | (CommunityCase.user_id == uid)
    ).count()

    rm = db.query(Member).filter(Member.user_id == uid).order_by(Member.created_at.desc()).limit(5).all()
    rc = db.query(Consultation).filter(Consultation.user_id == uid).order_by(Consultation.created_at.desc()).limit(5).all()

    return DashboardSummaryResponse(
        total_members=tm, total_consultations=tc, total_ai_reports=ta,
        total_healing_plans=th, total_community_cases=tcc,
        recent_members=[MemberResponse.model_validate(m) for m in rm],
        recent_consultations=[ConsultationResponse.model_validate(c) for c in rc],
    )
