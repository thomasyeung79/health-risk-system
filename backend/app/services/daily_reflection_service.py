"""Daily Reflection service — create reflections and generate weekly summaries.

Reflection fields:
  - What went well today?
  - Biggest challenge?
  - Gratitude
  - Notes
"""

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.daily_reflection import DailyReflection
from app.models.member import Member


def create_reflection(
    db: Session,
    user_id: int,
    member_id: int,
    went_well: str | None = None,
    biggest_challenge: str | None = None,
    gratitude: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Create a new daily reflection entry."""
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    reflection = DailyReflection(
        user_id=user_id,
        member_id=member_id,
        went_well=went_well,
        biggest_challenge=biggest_challenge,
        gratitude=gratitude,
        notes=notes,
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)

    return {
        "id": reflection.id,
        "member_id": reflection.member_id,
        "went_well": reflection.went_well,
        "biggest_challenge": reflection.biggest_challenge,
        "gratitude": reflection.gratitude,
        "notes": reflection.notes,
        "created_at": reflection.created_at.isoformat(),
    }


def list_reflections(
    db: Session,
    user_id: int,
    member_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    """List reflections, optionally filtered by member."""
    query = db.query(DailyReflection).filter(DailyReflection.user_id == user_id)
    if member_id is not None:
        query = query.filter(DailyReflection.member_id == member_id)
    total = query.count()
    items = query.order_by(DailyReflection.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "items": [
            {
                "id": r.id,
                "member_id": r.member_id,
                "went_well": r.went_well,
                "biggest_challenge": r.biggest_challenge,
                "gratitude": r.gratitude,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def generate_weekly_summary(
    db: Session,
    user_id: int,
    member_id: int,
) -> dict[str, Any]:
    """Generate a weekly summary of reflections for a member."""
    member = db.get(Member, member_id)
    if member is None:
        raise ValueError(f"Member {member_id} not found")

    is_cn = (member.preferred_language or "English") == "中文"

    week_ago = datetime.utcnow() - timedelta(days=7)
    week_start = week_ago.strftime("%Y-%m-%d")

    reflections = (
        db.query(DailyReflection)
        .filter(
            DailyReflection.user_id == user_id,
            DailyReflection.member_id == member_id,
            DailyReflection.created_at >= week_ago,
        )
        .order_by(DailyReflection.created_at.desc())
        .all()
    )

    if not reflections:
        if is_cn:
            return {
                "member_id": member_id,
                "week_start": week_start,
                "reflection_count": 0,
                "recurring_themes": [],
                "overall_theme": "本周暂无反思记录。",
                "suggestion": "建议每天花几分钟记录反思。",
            }
        return {
            "member_id": member_id,
            "week_start": week_start,
            "reflection_count": 0,
            "recurring_themes": [],
            "overall_theme": "No reflections recorded this week.",
            "suggestion": "Try spending a few minutes each day on reflection.",
        }

    # Extract keywords/themes from reflection texts
    all_text_parts: list[str] = []
    for r in reflections:
        if r.went_well:
            all_text_parts.append(r.went_well)
        if r.biggest_challenge:
            all_text_parts.append(r.biggest_challenge)
        if r.gratitude:
            all_text_parts.append(r.gratitude)

    # Simple keyword frequency
    stop_words = {"the", "a", "an", "to", "and", "of", "in", "it", "is", "was",
                  "that", "for", "on", "with", "my", "i", "me", "we", "be",
                  "了", "的", "是", "在", "和", "就", "我", "有", "不", "也", "要"}
    words: list[str] = []
    for text in all_text_parts:
        for w in text.lower().split():
            cleaned = w.strip(".,!?\"';:()[]")
            if cleaned and len(cleaned) > 2 and cleaned not in stop_words:
                words.append(cleaned)

    word_counts = Counter(words)
    common_words = [w for w, _ in word_counts.most_common(5) if word_counts[w] >= 2]

    if is_cn:
        recurring_themes = common_words if common_words else ["暂无明显重复主题"]
        overall_theme = (
            f"本周共记录了 {len(reflections)} 条反思。"
            f"美好时刻：{sum(1 for r in reflections if r.went_well)} 条，"
            f"感恩记录：{sum(1 for r in reflections if r.gratitude)} 条。"
        )
        suggestion = "继续坚持每日反思，帮助发现个人成长模式。"
    else:
        recurring_themes = common_words if common_words else ["No strong recurring themes yet"]
        overall_theme = (
            f"{len(reflections)} reflection(s) recorded this week. "
            f"{sum(1 for r in reflections if r.went_well)} highlights, "
            f"{sum(1 for r in reflections if r.gratitude)} gratitudes."
        )
        suggestion = "Keep up daily reflection to discover personal growth patterns."

    return {
        "member_id": member_id,
        "week_start": week_start,
        "reflection_count": len(reflections),
        "recurring_themes": recurring_themes,
        "overall_theme": overall_theme,
        "suggestion": suggestion,
    }
