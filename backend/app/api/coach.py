"""AI Coach API — generates daily coaching messages for members."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import CoachingMessageResponse
from app.services.ai_coach_service import generate_daily_message
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/coach", tags=["coach"])


@router.get("/daily/{member_id}", response_model=CoachingMessageResponse)
def get_daily_coaching(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a daily coaching message for a member."""
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = generate_daily_message(
        db=db, user_id=current_user.id, member_id=member_id,
    )
    return CoachingMessageResponse(**result)
