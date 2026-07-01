"""AI wellness report service — uses the pluggable AI provider layer."""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_report import AIReport
from app.models.member import Member
from app.services.ai_providers import create_ai_provider


def generate_wellness_report(
    db: Session,
    user_id: int,
    member_id: int,
    consultation_id: int | None = None,
) -> dict[str, Any]:
    """Generate a wellness report for a member via the configured AI provider.

    Uses the pluggable AI provider layer (rule_based by default).
    Falls back safely if the configured provider's API key is missing.
    No external API calls are made during tests.
    """
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    provider = create_ai_provider()
    content = provider.generate_report_content(member)

    report = AIReport(
        user_id=user_id,
        member_id=member_id,
        consultation_id=consultation_id,
        summary=content["summary"],
        risk_level=content["risk_level"],
        key_findings=json.dumps(content["key_findings"], ensure_ascii=False),
        recommendations=json.dumps(content["recommendations"], ensure_ascii=False),
        model_used=provider.model_name,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "member_id": report.member_id,
        "consultation_id": report.consultation_id,
        "summary": report.summary,
        "risk_level": report.risk_level,
        "key_findings": json.loads(report.key_findings) if report.key_findings else [],
        "recommendations": json.loads(report.recommendations) if report.recommendations else [],
        "model_used": report.model_used,
        "created_at": report.created_at.isoformat(),
    }
