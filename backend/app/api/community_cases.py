"""Community Case API routes — anonymised wellness case studies."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.community_case import CommunityCase
from app.models.user import User
from app.schemas.wellness_os import CommunityCaseCreate, CommunityCaseListResponse, CommunityCaseResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/community-cases", tags=["community-cases"])


@router.post("", response_model=CommunityCaseResponse, status_code=201)
def create_community_case(
    body: CommunityCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = CommunityCase(
        user_id=current_user.id, title=body.title, category=body.category,
        anonymized_summary=body.anonymized_summary, healing_approach=body.healing_approach,
        outcome=body.outcome, language=body.language, is_public=body.is_public,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=CommunityCaseListResponse)
def list_community_cases(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    public_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(CommunityCase)
    if public_only:
        query = query.filter(CommunityCase.is_public == True)
    else:
        query = query.filter(
            (CommunityCase.is_public == True) | (CommunityCase.user_id == current_user.id)
        )
    total = query.count()
    items = query.order_by(CommunityCase.created_at.desc()).offset(offset).limit(limit).all()
    return CommunityCaseListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{case_id}", response_model=CommunityCaseResponse)
def get_community_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.get(CommunityCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    if not case.is_public and case.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
