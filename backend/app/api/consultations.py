"""Consultation API routes."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consultation import Consultation
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import ConsultationCreate, ConsultationListResponse, ConsultationResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/consultations", tags=["consultations"])


@router.post("", response_model=ConsultationResponse, status_code=201)
def create_consultation(
    body: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, body.member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    qdata = json.dumps(body.questionnaire_data, ensure_ascii=False) if body.questionnaire_data else None
    c = Consultation(
        user_id=current_user.id, member_id=body.member_id,
        consultation_type=body.consultation_type, main_concern=body.main_concern,
        questionnaire_data=qdata, notes=body.notes,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("", response_model=ConsultationListResponse)
def list_consultations(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Consultation).filter(Consultation.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Consultation.created_at.desc()).offset(offset).limit(limit).all()
    return ConsultationListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = db.get(Consultation, consultation_id)
    if c is None or c.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return c
