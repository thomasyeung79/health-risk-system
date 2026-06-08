"""Metric trend analyzer — computes direction for individual metrics."""

from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.health_record import HealthRecord
from app.models.emotion_record import EmotionRecord
from app.services.trend_engine.config import METRICS, MetricDef


def compute_metric_trend(
    db: Session,
    user_id: int,
    metric_key: str,
    days: int = 7,
) -> dict[str, Any]:
    """Compute trend for a single metric over the given window.

    Returns:
      dict with keys: metric, current, previous, change, direction, higher_is_better
    """
    metric_def = METRICS.get(metric_key)
    if metric_def is None:
        return {
            "metric": metric_key,
            "current": None,
            "previous": None,
            "change": None,
            "direction": "unknown",
            "higher_is_better": True,
        }

    cutoff = datetime.utcnow() - timedelta(days=days)

    if metric_def.source == "health":
        records = (
            db.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user_id,
                HealthRecord.created_at >= cutoff,
            )
            .order_by(HealthRecord.created_at.asc())
            .all()
        )
        values = [getattr(r, metric_def.field) for r in records if getattr(r, metric_def.field) is not None]
    elif metric_def.source == "emotion":
        records = (
            db.query(EmotionRecord)
            .filter(
                EmotionRecord.user_id == user_id,
                EmotionRecord.created_at >= cutoff,
            )
            .order_by(EmotionRecord.created_at.asc())
            .all()
        )
        values = [getattr(r, metric_def.field) for r in records if getattr(r, metric_def.field) is not None]
    else:
        values = []

    if len(values) < 2:
        return {
            "metric": metric_key,
            "current": values[-1] if values else None,
            "previous": None,
            "change": None,
            "direction": "insufficient_data",
            "higher_is_better": metric_def.higher_is_better,
        }

    current = values[-1]
    previous = values[0]
    change = round(current - previous, 1)

    direction = _determine_direction(change, metric_def)
    return {
        "metric": metric_key,
        "current": current,
        "previous": previous,
        "change": change,
        "direction": direction,
        "higher_is_better": metric_def.higher_is_better,
    }


def _determine_direction(change: float, metric_def: MetricDef) -> str:
    """Determine improving/stable/declining based on change and metric config."""
    th = metric_def.threshold

    if abs(change) < th:
        return "stable"

    if metric_def.higher_is_better:
        return "improving" if change > 0 else "declining"
    else:
        return "improving" if change < 0 else "declining"
