"""Member profile API routes — CRUD for wellness members/clients."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import MemberCreate, MemberListResponse, MemberResponse, MemberUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/members", tags=["members"])


@router.post("", response_model=MemberResponse, status_code=201)
def create_member(
    body: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = Member(
        user_id=current_user.id, name=body.name, gender=body.gender,
        age=body.age, country=body.country,
        preferred_language=body.preferred_language,
        contact_info=body.contact_info, notes=body.notes,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=MemberListResponse)
def list_members(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Member).filter(Member.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Member.created_at.desc()).offset(offset).limit(limit).all()
    return MemberListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    body: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
