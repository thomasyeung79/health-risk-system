"""Cache logic for AI report engine — avoids redundant LLM calls."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.report_record import ReportRecord


def get_cached_report(
    db: Session,
    user_id: int,
    language: str,
    style: str,
    provider: str,
) -> Optional[ReportRecord]:
    """Return a cached report if one exists for today's date and same parameters."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    record = (
        db.query(ReportRecord)
        .filter(
            ReportRecord.user_id == user_id,
            ReportRecord.created_at >= today_start,
            ReportRecord.language == language,
            ReportRecord.style == style,
            ReportRecord.provider == provider,
        )
        .order_by(ReportRecord.created_at.desc())
        .first()
    )

    if record is not None:
        record.is_cached = True
        db.commit()

    return record


def save_report(
    db: Session,
    *,
    user_id: int,
    language: str,
    style: str,
    provider: str,
    model: str,
    health_record_id: Optional[int],
    emotion_record_id: Optional[int],
    days_analyzed: int,
    summary: str,
    sections: str,
    raw_output: str,
    tokens_used: int,
    latency_ms: int,
    is_fallback: bool,
) -> ReportRecord:
    """Persist a generated report to the database."""
    record = ReportRecord(
        user_id=user_id,
        language=language,
        style=style,
        provider=provider,
        model=model,
        health_record_id=health_record_id,
        emotion_record_id=emotion_record_id,
        days_analyzed=days_analyzed,
        summary=summary,
        sections=sections,
        raw_output=raw_output,
        tokens_used=tokens_used,
        latency_ms=latency_ms,
        is_cached=False,
        is_fallback=is_fallback,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
