"""Health check API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.health_record import HealthRecord
from app.schemas.health import (
    HealthCheckRequest,
    HealthCheckResponse,
    HealthRecordDetail,
    HealthRecordSummary,
    HealthRecordsResponse,
    HealthStatsResponse,
    ModuleResult,
    ModuleMap,
)
from app.services.health_check import run_health_check

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.post("/check", response_model=HealthCheckResponse)
def post_health_check(body: HealthCheckRequest, db: Session = Depends(get_db)):
    """Run a full health assessment and persist results."""
    result = run_health_check(
        db=db,
        language=body.language,
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        water_l=body.water_l,
        situation=body.situation,
        thirst_level=body.thirst_level,
        urine_color=body.urine_color,
        sleep_hours=body.sleep_hours,
        night_wake_times=body.night_wake_times,
        difficulty_falling_asleep=body.difficulty_falling_asleep,
        irregular_sleep_schedule=body.irregular_sleep_schedule,
        exercise_minutes=body.exercise_minutes,
        sedentary_hours=body.sedentary_hours,
        fruit_veg_servings=body.fruit_veg_servings,
        fast_food_times=body.fast_food_times,
        sugary_drinks=body.sugary_drinks,
        screen_time_hours=body.screen_time_hours,
        smoking=body.smoking,
        alcohol=body.alcohol,
        late_night=body.late_night,
        risk_score_emotion=body.risk_score_emotion,
        risk_score_focus=body.risk_score_focus,
        risk_score_body=body.risk_score_body,
    )

    modules_data = result["modules"]
    return HealthCheckResponse(
        id=result["id"],
        created_at=result["created_at"],
        language=result["language"],
        health_score=result["health_score"],
        risk_percent=result["risk_percent"],
        risk_level=result["risk_level"],
        modules=ModuleMap(
            **{
                name: ModuleResult(**data)
                for name, data in modules_data.items()
            }
        ),
        overall=result["overall"],
        primary_focus=result["primary_focus"],
        action_plan=result["action_plan"],
    )


@router.get("/records", response_model=HealthRecordsResponse)
def list_health_records(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List health records with pagination."""
    query = db.query(HealthRecord).order_by(HealthRecord.created_at.desc())
    total = query.count()
    records = query.offset(offset).limit(limit).all()

    items = [
        HealthRecordSummary(
            id=r.id,
            created_at=r.created_at.isoformat(),
            language=r.language,
            health_score=r.health_score,
            risk_percent=r.risk_percent,
            risk_level=r.risk_level,
        )
        for r in records
    ]

    return HealthRecordsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/records/{record_id}", response_model=HealthRecordDetail)
def get_health_record(record_id: int, db: Session = Depends(get_db)):
    """Get a single health record by ID."""
    record = db.get(HealthRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return HealthRecordDetail(
        id=record.id,
        created_at=record.created_at.isoformat(),
        language=record.language,
        weight_kg=record.weight_kg,
        height_cm=record.height_cm,
        water_l=record.water_l,
        situation=record.situation,
        thirst_level=record.thirst_level,
        urine_color=record.urine_color,
        sleep_hours=record.sleep_hours,
        night_wake_times=record.night_wake_times,
        difficulty_falling_asleep=record.difficulty_falling_asleep,
        irregular_sleep_schedule=record.irregular_sleep_schedule,
        exercise_minutes=record.exercise_minutes,
        sedentary_hours=record.sedentary_hours,
        fruit_veg_servings=record.fruit_veg_servings,
        fast_food_times=record.fast_food_times,
        sugary_drinks=record.sugary_drinks,
        screen_time_hours=record.screen_time_hours,
        smoking=record.smoking,
        alcohol=record.alcohol,
        late_night=record.late_night,
        risk_score_emotion=record.risk_score_emotion,
        risk_score_focus=record.risk_score_focus,
        risk_score_body=record.risk_score_body,
        bmi_score=record.bmi_score,
        water_score=record.water_score,
        sleep_score=record.sleep_score,
        activity_score=record.activity_score,
        diet_score=record.diet_score,
        mental_score=record.mental_score,
        screen_score=record.screen_score,
        habit_score=record.habit_score,
        health_score=record.health_score,
        risk_percent=record.risk_percent,
        risk_level=record.risk_level,
        risk_score=record.risk_score,
        interaction_score=record.interaction_score,
        overall=record.overall,
        primary_focus=record.primary_focus,
        action_plan=record.action_plan,
    )


@router.get("/stats", response_model=HealthStatsResponse)
def get_health_stats(db: Session = Depends(get_db)):
    """Get aggregated health statistics."""
    total = db.query(HealthRecord).count()

    avg = db.query(func.avg(HealthRecord.health_score)).scalar()
    average_health_score = round(avg, 1) if avg is not None else None

    latest = (
        db.query(HealthRecord.risk_level)
        .order_by(HealthRecord.created_at.desc())
        .first()
    )
    latest_risk_level = latest[0] if latest else None

    return HealthStatsResponse(
        total_records=total,
        average_health_score=average_health_score,
        latest_risk_level=latest_risk_level,
    )
