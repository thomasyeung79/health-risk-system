"""Deterministic AI wellness report service — rule-based, no external API calls."""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.ai_report import AIReport
from app.models.member import Member


def generate_wellness_report(
    db: Session,
    user_id: int,
    member_id: int,
    consultation_id: int | None = None,
) -> dict[str, Any]:
    """Generate a rule-based wellness report for a member.

    This is a deterministic placeholder service.
    No external API calls are made.
    Easy to swap for OpenAI/DeepSeek later.
    """
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    lang = member.preferred_language or "English"
    is_cn = lang == "中文"

    age = member.age or 30
    if age >= 60:
        risk_level = "High" if not is_cn else "高"
    elif age >= 40:
        risk_level = "Medium" if not is_cn else "中"
    else:
        risk_level = "Low" if not is_cn else "低"

    if is_cn:
        summary = (
            f"{member.name} 的健康评估已完成。"
            f"年龄 {age} 岁，当前风险等级为「{risk_level}」。"
            "建议定期进行健康检测，保持均衡饮食和适度运动。"
        )
        findings = [
            f"年龄因素：{age} 岁",
            f"风险等级：{risk_level}",
            "建议每季度进行一次全面健康检测",
        ]
        recommendations = [
            "保持规律作息，每天睡眠 7-8 小时",
            "每周进行至少 150 分钟中等强度运动",
            "饮食以蔬菜、水果、全谷物为主",
            "定期记录健康数据，跟踪变化趋势",
        ]
    else:
        summary = (
            f"Wellness assessment completed for {member.name}. "
            f"Age {age}, current risk level: {risk_level}. "
            "Regular health check-ups, balanced diet, and moderate exercise are recommended."
        )
        findings = [
            f"Age factor: {age} years",
            f"Risk level: {risk_level}",
            "Quarterly comprehensive health check recommended",
        ]
        recommendations = [
            "Maintain consistent sleep schedule (7-8 hours)",
            "At least 150 minutes of moderate exercise per week",
            "Focus on vegetables, fruits, and whole grains",
            "Track health data regularly to monitor trends",
        ]

    report = AIReport(
        user_id=user_id,
        member_id=member_id,
        consultation_id=consultation_id,
        summary=summary,
        risk_level=risk_level,
        key_findings=json.dumps(findings, ensure_ascii=False),
        recommendations=json.dumps(recommendations, ensure_ascii=False),
        model_used="wellness-os-rules-v1",
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
