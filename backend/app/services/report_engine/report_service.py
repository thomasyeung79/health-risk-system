"""Report orchestration service — coordinates ContextBuilder, Provider, Cache."""

import json
import time
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.services.report_engine.cache import get_cached_report, save_report
from app.services.report_engine.context_builder import build_context
from app.services.report_engine.provider import create_provider
from app.services.report_engine.prompts import get_system_prompt, get_user_prompt
from app.services.report_engine.response_parser import parse_response


def generate_report(
    db: Session,
    user_id: int,
    language: str,
    style: str = "balanced",
    days: int = 7,
    health_record_id: Optional[int] = None,
    emotion_record_id: Optional[int] = None,
) -> dict[str, Any]:
    """Generate a wellness report with caching and automatic fallback."""
    provider_obj = create_provider()

    # 1. Check cache
    cached = get_cached_report(
        db=db,
        user_id=user_id,
        language=language,
        style=style,
        provider=provider_obj.provider_name,
    )
    if cached is not None:
        sections_data = cached.sections or "[]"
        try:
            sections = json.loads(sections_data)
        except (json.JSONDecodeError, TypeError):
            sections = []
        return {
            "id": cached.id,
            "created_at": cached.created_at.isoformat(),
            "language": cached.language,
            "style": cached.style,
            "provider": cached.provider,
            "model": cached.model or "",
            "is_cached": True,
            "is_fallback": cached.is_fallback,
            "report": {
                "summary": cached.summary or "",
                "sections": sections,
            },
            "token_usage": {
                "total": cached.tokens_used or 0,
                "cost_estimate": 0.0,
            },
        }

    # 2. Build context
    context = build_context(
        db=db,
        user_id=user_id,
        language=language,
        style=style,
        days=days,
        health_record_id=health_record_id,
        emotion_record_id=emotion_record_id,
    )

    # 3. Prepare prompts
    system_prompt = get_system_prompt(language, style)
    user_prompt = get_user_prompt(context)

    # 4. Generate with automatic fallback
    start_time = time.time()
    is_fallback = False
    tokens_used = 0

    try:
        raw_output = provider_obj.generate(system_prompt, user_prompt)
        tokens_used = getattr(provider_obj, "last_tokens_used", 0)
    except Exception:
        from app.services.report_engine.local_provider import LocalProvider
        fallback = LocalProvider()
        raw_output = fallback.generate(system_prompt, user_prompt)
        is_fallback = True

    latency_ms = int((time.time() - start_time) * 1000)

    # 5. Parse response
    parsed = parse_response(raw_output, language)

    # 6. Persist
    record = save_report(
        db=db,
        user_id=user_id,
        language=language,
        style=style,
        provider=provider_obj.provider_name,
        model=provider_obj.model_name(),
        health_record_id=health_record_id,
        emotion_record_id=emotion_record_id,
        days_analyzed=days,
        summary=parsed["summary"],
        sections=json.dumps(parsed["sections"], ensure_ascii=False),
        raw_output=raw_output,
        tokens_used=tokens_used,
        latency_ms=latency_ms,
        is_fallback=is_fallback,
    )

    cost = (
        round(tokens_used / 1000 * provider_obj.cost_per_1k_tokens, 6)
        if tokens_used > 0
        else 0.0
    )

    return {
        "id": record.id,
        "created_at": record.created_at.isoformat(),
        "language": record.language,
        "style": record.style,
        "provider": record.provider,
        "model": record.model or "",
        "is_cached": False,
        "is_fallback": record.is_fallback,
        "report": {
            "summary": parsed["summary"],
            "sections": parsed["sections"],
        },
        "token_usage": {
            "total": tokens_used,
            "cost_estimate": cost,
        },
    }
