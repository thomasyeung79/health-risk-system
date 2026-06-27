"""AI Report API routes — generate and list wellness reports for members."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_report import AIReport
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import AIReportGenerateRequest, AIReportListResponse, AIReportResponse
from app.services.ai_report_service import generate_wellness_report
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/ai-reports", tags=["ai-reports"])


@router.post("/generate", response_model=AIReportResponse, status_code=201)
def post_generate_report(
    body: AIReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, body.member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = generate_wellness_report(
        db=db, user_id=current_user.id,
        member_id=body.member_id, consultation_id=body.consultation_id,
    )
    return AIReportResponse(**result)


@router.get("", response_model=AIReportListResponse)
def list_ai_reports(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AIReport).filter(AIReport.user_id == current_user.id)
    total = query.count()
    items = query.order_by(AIReport.created_at.desc()).offset(offset).limit(limit).all()
    return AIReportListResponse(items=items, total=total, limit=limit, offset=offset)
