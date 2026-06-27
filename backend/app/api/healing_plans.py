"""Healing Plan API routes — CRUD for member wellness plans."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.healing_plan import HealingPlan
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import (
    HealingPlanCreate,
    HealingPlanListResponse,
    HealingPlanResponse,
    HealingPlanUpdate,
)
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/healing-plans", tags=["healing-plans"])


@router.post("", response_model=HealingPlanResponse, status_code=201)
def create_healing_plan(
    body: HealingPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.get(Member, body.member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    pitems = json.dumps(body.plan_items, ensure_ascii=False) if body.plan_items else None
    plan = HealingPlan(
        user_id=current_user.id, member_id=body.member_id,
        title=body.title, description=body.description,
        plan_items=pitems, status=body.status,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=HealingPlanListResponse)
def list_healing_plans(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(HealingPlan).filter(HealingPlan.user_id == current_user.id)
    total = query.count()
    items = query.order_by(HealingPlan.created_at.desc()).offset(offset).limit(limit).all()
    return HealingPlanListResponse(items=items, total=total, limit=limit, offset=offset)


@router.patch("/{plan_id}", response_model=HealingPlanResponse)
def update_healing_plan(
    plan_id: int,
    body: HealingPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.get(HealingPlan, plan_id)
    if plan is None or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        if key == "plan_items" and value is not None:
            value = json.dumps(value, ensure_ascii=False)
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan
