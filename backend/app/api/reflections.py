"""Daily Reflection API — create, list and generate weekly summaries of reflections."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import (
    ReflectionCreate,
    ReflectionListResponse,
    ReflectionResponse,
    WeeklySummaryResponse,
)
from app.services.auth import get_current_user
from app.services.daily_reflection_service import (
    create_reflection,
    generate_weekly_summary,
    list_reflections,
)

router = APIRouter(prefix="/api/v1/reflections", tags=["reflections"])


@router.post("", response_model=ReflectionResponse, status_code=201)
def post_reflection(
    body: ReflectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new daily reflection entry."""
    member = db.get(Member, body.member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = create_reflection(
        db=db,
        user_id=current_user.id,
        member_id=body.member_id,
        went_well=body.went_well,
        biggest_challenge=body.biggest_challenge,
        gratitude=body.gratitude,
        notes=body.notes,
    )
    return ReflectionResponse(**result)


@router.get("", response_model=ReflectionListResponse)
def get_reflections(
    member_id: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List daily reflections, optionally filtered by member."""
    result = list_reflections(
        db=db, user_id=current_user.id,
        member_id=member_id, limit=limit, offset=offset,
    )
    return ReflectionListResponse(**result)


@router.get("/weekly-summary/{member_id}", response_model=WeeklySummaryResponse)
def get_weekly_summary(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a weekly summary of reflections for a member."""
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = generate_weekly_summary(
        db=db, user_id=current_user.id, member_id=member_id,
    )
    return WeeklySummaryResponse(**result)
