"""Trend orchestration service — computes overall trend summary."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.health_record import HealthRecord
from app.models.emotion_record import EmotionRecord
from app.services.trend_engine.config import METRICS
from app.services.trend_engine.metric_analyzer import compute_metric_trend


def compute_summary(
    db: Session,
    days: int = 7,
    language: str = "English",
) -> dict[str, Any]:
    """Compute an overall trend summary for 4 core metrics."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    health_count = (
        db.query(HealthRecord)
        .filter(HealthRecord.created_at >= cutoff)
        .count()
    )
    emotion_count = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.created_at >= cutoff)
        .count()
    )

    metric_keys = ["health_score", "stress", "energy", "sleep_score"]
    metrics = [compute_metric_trend(db, k, days) for k in metric_keys]

    # Overall direction: majority vote
    direction_counts: dict[str, int] = {}
    for m in metrics:
        d = m["direction"]
        if d in ("improving", "declining", "stable"):
            direction_counts[d] = direction_counts.get(d, 0) + 1

    if direction_counts:
        overall_dir = max(direction_counts, key=direction_counts.get)
    else:
        overall_dir = "insufficient_data"

    return {
        "days_analyzed": days,
        "health_data_points": health_count,
        "emotion_data_points": emotion_count,
        "overall_direction": overall_dir,
        "metrics": metrics,
    }
