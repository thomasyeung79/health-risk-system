"""Insights Dashboard API — generates meaningful wellness insights for a member."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import InsightsResponse
from app.services.auth import get_current_user
from app.services.insights_service import generate_insights

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


@router.get("/{member_id}", response_model=InsightsResponse)
def get_insights(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate insights for a member."""
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = generate_insights(db=db, user_id=current_user.id, member_id=member_id)
    return InsightsResponse(**result)
