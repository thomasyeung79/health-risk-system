"""Emotion analysis API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.emotion_record import EmotionRecord
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.emotion import (
    EmotionAnalyzeRequest,
    EmotionAnalyzeResponse,
    EmotionalPattern,
    Guidance,
    BreathingPractice,
    EmotionRecordSummary,
    EmotionRecordDetail,
    EmotionRecordsResponse,
    EmotionStatsResponse,
)
from app.services.emotion_analysis import analyze_emotion

router = APIRouter(prefix="/api/v1/emotion", tags=["emotion"])


@router.post("/analyze", response_model=EmotionAnalyzeResponse)
def post_emotion_analyze(
    body: EmotionAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run emotion analysis and persist results."""
    result = analyze_emotion(
        db=db,
        user_id=current_user.id,
        language=body.language,
        mood_key=body.mood_key,
        event_key=body.event_key,
        energy=body.energy,
        stress=body.stress,
    )

    return EmotionAnalyzeResponse(
        id=result["id"],
        created_at=result["created_at"],
        language=result["language"],
        summary=result["summary"],
        pattern=EmotionalPattern(**result["pattern"]),
        matched_topic=result["matched_topic"],
        tonight=result["tonight"],
        tomorrow=result["tomorrow"],
        guidance=Guidance(**result["guidance"]),
        breathing=BreathingPractice(**result["breathing"]),
        full_story=result["full_story"],
    )


@router.get("/records", response_model=EmotionRecordsResponse)
def list_emotion_records(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List emotion records with pagination."""
    query = db.query(EmotionRecord).filter(
        EmotionRecord.user_id == current_user.id
    ).order_by(EmotionRecord.created_at.desc())
    total = query.count()
    records = query.offset(offset).limit(limit).all()

    items = [
        EmotionRecordSummary(
            id=r.id,
            created_at=r.created_at.isoformat(),
            language=r.language,
            mood_key=r.mood_key,
            event_key=r.event_key,
            energy=r.energy,
            stress=r.stress,
            pattern_key=r.pattern_key,
        )
        for r in records
    ]

    return EmotionRecordsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/records/{record_id}", response_model=EmotionRecordDetail)
def get_emotion_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single emotion record by ID."""
    record = db.get(EmotionRecord, record_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Record not found")

    return EmotionRecordDetail(
        id=record.id,
        created_at=record.created_at.isoformat(),
        language=record.language,
        mood_key=record.mood_key,
        event_key=record.event_key,
        energy=record.energy,
        stress=record.stress,
        pattern_key=record.pattern_key,
        pattern_severity=record.pattern_severity,
        summary=record.summary,
        topic_key=record.topic_key,
        tonight=record.tonight,
        tomorrow=record.tomorrow,
        breathing_type=record.breathing_type,
        full_story=record.full_story,
    )


@router.get("/stats", response_model=EmotionStatsResponse)
def get_emotion_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated emotion statistics."""
    base = db.query(EmotionRecord).filter(EmotionRecord.user_id == current_user.id)
    total = base.count()

    avg_energy = base.with_entities(func.avg(EmotionRecord.energy)).scalar()
    avg_stress = base.with_entities(func.avg(EmotionRecord.stress)).scalar()

    latest = (
        base.with_entities(EmotionRecord.mood_key)
        .order_by(EmotionRecord.created_at.desc())
        .first()
    )

    return EmotionStatsResponse(
        total_records=total,
        average_energy=round(avg_energy, 1) if avg_energy is not None else None,
        average_stress=round(avg_stress, 1) if avg_stress is not None else None,
        latest_mood=latest[0] if latest else None,
    )
