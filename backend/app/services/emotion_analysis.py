"""Emotion analysis orchestration service.

Calls the emotion engine, persists results to the database,
and returns structured output.
"""
from typing import Any

from sqlalchemy.orm import Session

from app.engines.emotion import run_reflection_engine
from app.models.emotion_record import EmotionRecord


def analyze_emotion(
    db: Session,
    user_id: int,
    language: str,
    *,
    mood_key: str,
    event_key: str,
    energy: int,
    stress: int,
) -> dict[str, Any]:
    """Run emotion analysis and persist results."""
    result = run_reflection_engine(
        clean_mood=[mood_key],
        clean_things=[event_key],
        stress_level=stress,
        energy_level=energy,
        language=language,
    )

    record = EmotionRecord(
        user_id=user_id,
        language=language,
        mood_key=mood_key,
        event_key=event_key,
        energy=energy,
        stress=stress,
        pattern_key=result["pattern"]["pattern"],
        pattern_severity=result["pattern"]["severity"],
        summary=result["summary"],
        topic_key=result["matched_topic_key"],
        tonight=result["tonight"],
        tomorrow=result["tomorrow"],
        breathing_type=result["breathing"]["type"],
        full_story=result["story"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "created_at": record.created_at.isoformat(),
        "language": language,
        "summary": result["summary"],
        "pattern": result["pattern"],
        "matched_topic": result["matched_topic"],
        "tonight": result["tonight"],
        "tomorrow": result["tomorrow"],
        "guidance": result["guidance"],
        "breathing": result["breathing"],
        "full_story": result["story"],
    }
