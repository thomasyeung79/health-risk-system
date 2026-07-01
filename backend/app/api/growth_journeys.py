"""Growth Journey API routes — generate, list, and view wellness growth timelines."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.growth_journey import GrowthJourney
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import (
    GrowthJourneyGenerateRequest,
    GrowthJourneyListResponse,
    GrowthJourneyResponse,
)
from app.services.auth import get_current_user
from app.services.growth_journey_service import generate_growth_journey

router = APIRouter(prefix="/api/v1/growth-journeys", tags=["growth-journeys"])


@router.get("", response_model=GrowthJourneyListResponse)
def list_growth_journeys(
    member_id: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List growth journeys for the current user, optionally filtered by member."""
    query = db.query(GrowthJourney).filter(GrowthJourney.user_id == current_user.id)
    if member_id is not None:
        query = query.filter(GrowthJourney.member_id == member_id)
    total = query.count()
    items = query.order_by(GrowthJourney.created_at.desc()).offset(offset).limit(limit).all()
    return GrowthJourneyListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/generate", response_model=GrowthJourneyResponse, status_code=201)
def post_generate_journey(
    body: GrowthJourneyGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new growth journey for a member."""
    member = db.get(Member, body.member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = generate_growth_journey(
        db=db, user_id=current_user.id, member_id=body.member_id,
    )
    return GrowthJourneyResponse(**result)


@router.get("/{journey_id}", response_model=GrowthJourneyResponse)
def get_growth_journey(
    journey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single growth journey by ID."""
    journey = db.get(GrowthJourney, journey_id)
    if journey is None or journey.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Growth journey not found")
    return GrowthJourneyResponse(
        id=journey.id,
        member_id=journey.member_id,
        title=journey.title,
        summary=journey.summary,
        timeline_items=json.loads(journey.timeline_items) if journey.timeline_items else [],
        insights=json.loads(journey.insights) if journey.insights else {},
        created_at=journey.created_at,
        updated_at=journey.updated_at,
    )
