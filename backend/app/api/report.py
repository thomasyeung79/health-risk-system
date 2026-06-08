"""Wellness report API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report_record import ReportRecord
from app.models.user import User
from app.services.auth import get_current_user
from app.schemas.report import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportContent,
    ReportListResponse,
    ReportSection,
    ReportSummary,
    TokenUsage,
)
from app.services.report_engine.report_service import generate_report

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("/generate", response_model=GenerateReportResponse)
def post_generate_report(
    body: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a wellness report from health + emotion data."""
    result = generate_report(
        db=db,
        user_id=current_user.id,
        language=body.language,
        style=body.style,
        days=body.days,
        health_record_id=body.health_record_id,
        emotion_record_id=body.emotion_record_id,
    )
    return GenerateReportResponse(
        id=result["id"],
        created_at=result["created_at"],
        language=result["language"],
        style=result["style"],
        provider=result["provider"],
        model=result["model"],
        is_cached=result["is_cached"],
        is_fallback=result["is_fallback"],
        report=ReportContent(
            summary=result["report"]["summary"],
            sections=[
                ReportSection(**s) for s in result["report"]["sections"]
            ],
        ),
        token_usage=TokenUsage(**result["token_usage"]),
    )


@router.get("", response_model=ReportListResponse)
def list_reports(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List generated reports with pagination."""
    query = db.query(ReportRecord).filter(
        ReportRecord.user_id == current_user.id
    ).order_by(ReportRecord.created_at.desc())
    total = query.count()
    records = query.offset(offset).limit(limit).all()

    items = [
        ReportSummary(
            id=r.id,
            created_at=r.created_at.isoformat(),
            language=r.language,
            style=r.style or "",
            provider=r.provider or "",
            is_cached=r.is_cached,
            is_fallback=r.is_fallback,
            summary=(r.summary or "")[:200],
        )
        for r in records
    ]

    return ReportListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{report_id}", response_model=GenerateReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single report by ID."""
    record = db.get(ReportRecord, report_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")

    import json
    sections_data = record.sections or "[]"
    try:
        sections = json.loads(sections_data)
    except (json.JSONDecodeError, TypeError):
        sections = []

    return GenerateReportResponse(
        id=record.id,
        created_at=record.created_at.isoformat(),
        language=record.language,
        style=record.style or "",
        provider=record.provider or "",
        model=record.model or "",
        is_cached=record.is_cached,
        is_fallback=record.is_fallback,
        report=ReportContent(
            summary=record.summary or "",
            sections=[ReportSection(**s) for s in sections],
        ),
        token_usage=TokenUsage(
            total=record.tokens_used or 0,
            cost_estimate=0.0,
        ),
    )
