"""Context Builder — transforms raw health & emotion data into structured LLM input.

This module does NOT call any LLM. It only aggregates and summarizes data
for downstream providers.
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.health_record import HealthRecord
from app.models.emotion_record import EmotionRecord


def build_context(
    db: Session,
    language: str,
    style: str = "balanced",
    days: int = 7,
    health_record_id: Optional[int] = None,
    emotion_record_id: Optional[int] = None,
) -> dict[str, Any]:
    """Build a structured context dict from health and emotion data.

    Returns a dict with keys:
      - language, style
      - health_summary, emotion_summary
      - trends, correlations, flags
      - has_health_data, has_emotion_data
    """
    context: dict[str, Any] = {
        "language": language,
        "style": style,
        "days": days,
        "health_summary": None,
        "emotion_summary": None,
        "trends": [],
        "correlations": [],
        "flags": [],
        "has_health_data": False,
        "has_emotion_data": False,
    }

    # Fetch latest records
    latest_health: Optional[HealthRecord] = None
    latest_emotion: Optional[EmotionRecord] = None

    if health_record_id:
        latest_health = db.get(HealthRecord, health_record_id)
    else:
        latest_health = (
            db.query(HealthRecord)
            .order_by(HealthRecord.created_at.desc())
            .first()
        )

    if emotion_record_id:
        latest_emotion = db.get(EmotionRecord, emotion_record_id)
    else:
        latest_emotion = (
            db.query(EmotionRecord)
            .order_by(EmotionRecord.created_at.desc())
            .first()
        )

    # Health summary
    if latest_health:
        context["has_health_data"] = True
        context["health_summary"] = {
            "health_score": latest_health.health_score,
            "risk_level": latest_health.risk_level,
            "risk_percent": latest_health.risk_percent,
            "modules": {
                "BMI": latest_health.bmi_score,
                "Water": latest_health.water_score,
                "Sleep": latest_health.sleep_score,
                "Activity": latest_health.activity_score,
                "Diet": latest_health.diet_score,
                "Mental": latest_health.mental_score,
                "Screen": latest_health.screen_score,
                "Habit": latest_health.habit_score,
            },
            "primary_focus": latest_health.primary_focus,
        }

        # Trend data: compare with earlier records
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_records = (
            db.query(HealthRecord)
            .filter(HealthRecord.created_at >= cutoff)
            .order_by(HealthRecord.created_at.asc())
            .all()
        )
        if len(recent_records) >= 2:
            first = recent_records[0]
            last = recent_records[-1]
            change = round((last.health_score or 0) - (first.health_score or 0), 1)
            direction = "improving" if change > 2 else ("declining" if change < -2 else "stable")
            context["trends"].append({
                "type": "health",
                "direction": direction,
                "change": change,
                "first_score": first.health_score,
                "last_score": last.health_score,
            })

    # Emotion summary
    if latest_emotion:
        context["has_emotion_data"] = True
        context["emotion_summary"] = {
            "mood_key": latest_emotion.mood_key,
            "stress": latest_emotion.stress,
            "energy": latest_emotion.energy,
            "pattern_key": latest_emotion.pattern_key,
            "pattern_severity": latest_emotion.pattern_severity,
        }

        # Emotion trend
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_emotions = (
            db.query(EmotionRecord)
            .filter(EmotionRecord.created_at >= cutoff)
            .order_by(EmotionRecord.created_at.asc())
            .all()
        )
        if recent_emotions:
            avg_stress = sum(r.stress or 0 for r in recent_emotions) / len(recent_emotions)
            avg_energy = sum(r.energy or 0 for r in recent_emotions) / len(recent_emotions)
            context["emotion_summary"]["avg_stress"] = round(avg_stress, 1)
            context["emotion_summary"]["avg_energy"] = round(avg_energy, 1)

    # Cross correlations (simple heuristics)
    if latest_health and latest_emotion:
        if (latest_health.sleep_score or 0) >= 2 and (latest_emotion.stress or 0) >= 7:
            context["correlations"].append({
                "type": "sleep_stress",
                "description": "High stress may be affecting sleep quality."
                if language == "English" else "高压力可能正在影响睡眠质量。",
            })
        if (latest_health.activity_score or 0) >= 2 and (latest_emotion.energy or 0) <= 3:
            context["correlations"].append({
                "type": "activity_energy",
                "description": "Low activity levels may be contributing to low energy."
                if language == "English" else "活动量不足可能导致能量偏低。",
            })

    # Flags
    if latest_health:
        for module_name, score in context["health_summary"]["modules"].items():
            if score is not None and score >= 3:
                context["flags"].append(
                    f"High risk in {module_name}: score {score}/3"
                    if language == "English"
                    else f"高风险模块 {module_name}：评分 {score}/3"
                )
    if latest_emotion and (latest_emotion.stress or 0) >= 8:
        context["flags"].append(
            f"Stress level is very high: {latest_emotion.stress}/10"
            if language == "English"
            else f"压力水平很高：{latest_emotion.stress}/10"
        )

    return context
