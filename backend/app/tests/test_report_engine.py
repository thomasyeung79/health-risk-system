"""Tests for the report engine: context builder, provider, cache, service."""

import json
from unittest.mock import ANY, MagicMock, patch

import pytest

from app.models.report_record import ReportRecord
from app.services.report_engine.cache import get_cached_report, save_report
from app.services.report_engine.context_builder import build_context
from app.services.report_engine.deepseek_provider import DeepSeekProvider
from app.services.report_engine.local_provider import LocalProvider
from app.services.report_engine.provider import create_provider
from app.services.report_engine.prompts import get_system_prompt, get_user_prompt
from app.services.report_engine.response_parser import parse_response
from app.services.report_engine.report_service import generate_report


class TestContextBuilder:
    def test_empty_db(self, db_session):
        ctx = build_context(db_session, 1, "English")
        assert ctx["has_health_data"] is False
        assert ctx["has_emotion_data"] is False
        assert ctx["health_summary"] is None

    def test_with_health_data(self, db_session):
        from app.models.health_record import HealthRecord
        db_session.add(HealthRecord(user_id=1, health_score=85.0, risk_level="Low Risk", language="English"))
        db_session.flush()
        ctx = build_context(db_session, 1, "English")
        assert ctx["has_health_data"] is True
        assert ctx["health_summary"]["health_score"] == 85.0

    def test_with_emotion_data(self, db_session):
        from app.models.emotion_record import EmotionRecord
        db_session.add(EmotionRecord(user_id=1, mood_key="Calm", stress=3, energy=7, language="English"))
        db_session.flush()
        ctx = build_context(db_session, 1, "English")
        assert ctx["has_emotion_data"] is True
        assert ctx["emotion_summary"]["mood_key"] == "Calm"

    def test_chinese(self, db_session):
        ctx = build_context(db_session, 1, "中文")
        assert ctx["language"] == "中文"

    def test_high_risk_flags(self, db_session):
        from app.models.health_record import HealthRecord
        db_session.add(HealthRecord(
            user_id=1, health_score=30.0, risk_level="High Risk", language="English",
            sleep_score=3, bmi_score=3,
        ))
        db_session.flush()
        ctx = build_context(db_session, 1, "English")
        assert len(ctx["flags"]) >= 2


class TestProvider:
    def test_create_no_key(self):
        with patch.dict("os.environ", {}, clear=True):
            p = create_provider()
            assert p.provider_name == "local"

    def test_create_with_key(self):
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test"}):
            p = create_provider()
            assert p.provider_name == "deepseek"

    def test_local_output_old_format(self):
        p = LocalProvider()
        r = p.generate("system", "health_score: 85, risk_level: Low Risk")
        assert len(r) > 0

    def test_local_output_english_rendered(self):
        """Rendered English prompt format (how ContextBuilder actually outputs it)."""
        p = LocalProvider()
        ctx = "Generate a comprehensive wellness report based on this data:\n\nHealth Score: 85.0/100\nRisk Level: Low Risk\nModule Scores:\n  - BMI: 0/3\n  - Sleep: 1/3"
        r = p.generate("system", ctx)
        assert "not enough" not in r.lower()
        assert len(r) > 0

    def test_local_output_chinese_rendered(self):
        """Rendered Chinese prompt format."""
        p = LocalProvider()
        ctx = "请基于以下健康数据生成综合报告：\n\n健康评分: 85/100\n风险等级: 低风险\n模块评分:\n  - BMI: 0/3\n  - 睡眠: 1/3"
        r = p.generate("system", ctx)
        assert "没有足够的" not in r
        assert len(r) > 0

    def test_local_no_data(self):
        p = LocalProvider()
        r = p.generate("system", "")
        assert "data" in r.lower() or "数据" in r

    def test_deepseek_mocked(self):
        p = DeepSeekProvider(api_key="sk-test")
        mock = MagicMock()
        mock.choices[0].message.content = "Mocked report"
        mock.usage.total_tokens = 50
        p._client.chat.completions.create = MagicMock(return_value=mock)
        r = p.generate("system", "ctx")
        assert r == "Mocked report"
        assert p.last_tokens_used == 50


class TestPrompts:
    def test_english(self):
        p = get_system_prompt("English", "balanced")
        assert "Wellness Analyst" in p

    def test_chinese(self):
        p = get_system_prompt("中文", "balanced")
        assert "健康分析师" in p

    def test_user_prompt(self):
        ctx = {"language": "English", "health_summary": {"health_score": 85.0, "risk_level": "Low Risk", "modules": {"Sleep": 2}}, "emotion_summary": None}
        p = get_user_prompt(ctx)
        assert "85.0" in p


class TestParser:
    def test_markdown_sections(self):
        o = "Sum\n\n## Health\nGood.\n## Emotion\nStable.\n## Actions\nSleep."
        r = parse_response(o, "English")
        assert len(r["sections"]) == 3

    def test_plain_text(self):
        r = parse_response("Plain text.", "English")
        assert len(r["sections"]) == 1

    def test_empty(self):
        r = parse_response("", "English")
        assert r["summary"] == ""


class TestCache:
    def test_miss(self, db_session):
        r = get_cached_report(db_session, 1, "English", "balanced", "local")
        assert r is None

    def test_hit(self, db_session):
        save_report(db=db_session, user_id=1, language="English", style="balanced", provider="local",
                     model="t", health_record_id=None, emotion_record_id=None,
                     days_analyzed=7, summary="Cached", sections="[]", raw_output="t",
                     tokens_used=0, latency_ms=0, is_fallback=True)
        r = get_cached_report(db_session, 1, "English", "balanced", "local")
        assert r is not None

    def test_save_fields(self, db_session):
        r = save_report(db=db_session, user_id=1, language="English", style="coaching", provider="deepseek",
                         model="dc", health_record_id=1, emotion_record_id=2,
                         days_analyzed=7, summary="S", sections="[]", raw_output="R",
                         tokens_used=150, latency_ms=500, is_fallback=False)
        assert r.provider == "deepseek"
        assert r.tokens_used == 150
        assert r.latency_ms == 500
        assert r.is_cached is False
        assert r.is_fallback is False


class TestReportService:
    def test_no_api_key(self, db_session):
        with patch.dict("os.environ", {}, clear=True):
            r = generate_report(db_session, 1, "English", "balanced")
            assert r["provider"] == "local"
            assert r["is_fallback"] is False
            assert r["report"]["summary"] is not None

    def test_with_health_data(self, db_session):
        from app.models.health_record import HealthRecord
        db_session.add(HealthRecord(user_id=1, health_score=85.0, risk_level="Low Risk", language="English"))
        db_session.flush()
        with patch.dict("os.environ", {}, clear=True):
            r = generate_report(db_session, 1, "English", "balanced")
            assert r["report"]["summary"] is not None

    def test_chinese(self, db_session):
        with patch.dict("os.environ", {}, clear=True):
            r = generate_report(db_session, 1, "中文", "balanced")
            assert r["language"] == "中文"

    def test_cache_on_second_call(self, db_session):
        with patch.dict("os.environ", {}, clear=True):
            r1 = generate_report(db_session, 1, "English", "balanced")
            r2 = generate_report(db_session, 1, "English", "balanced")
            assert r2["is_cached"] is True
            assert r2["id"] == r1["id"]

    def test_different_style_no_cache(self, db_session):
        with patch.dict("os.environ", {}, clear=True):
            r1 = generate_report(db_session, 1, "English", "balanced")
            r2 = generate_report(db_session, 1, "English", "coaching")
            assert r2["is_cached"] is False



