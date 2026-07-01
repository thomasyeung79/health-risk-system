"""Tests for the pluggable AI provider layer — fallback, factory, and model name."""

import os
from unittest.mock import patch

import pytest

from app.services.ai_providers import (
    DeepSeekProvider,
    OpenAIProvider,
    RuleBasedProvider,
    create_ai_provider,
)


class TestRuleBasedProvider:
    """Unit tests for the rule-based AI provider."""

    def test_generates_report_content(self):
        member = FakeMember("Alice", 35, "English")
        provider = RuleBasedProvider()
        content = provider.generate_report_content(member)

        assert "summary" in content
        assert "risk_level" in content
        assert "key_findings" in content
        assert "recommendations" in content
        assert content["risk_level"] == "Low"
        assert "Alice" in content["summary"]

    def test_high_risk_for_older_age(self):
        member = FakeMember("Bob", 65, "English")
        provider = RuleBasedProvider()
        content = provider.generate_report_content(member)
        assert content["risk_level"] == "High"

    def test_medium_risk_for_mid_age(self):
        member = FakeMember("Carol", 45, "English")
        provider = RuleBasedProvider()
        content = provider.generate_report_content(member)
        assert content["risk_level"] == "Medium"

    def test_chinese_output(self):
        member = FakeMember("张三", 50, "中文")
        provider = RuleBasedProvider()
        content = provider.generate_report_content(member)
        assert content["risk_level"] == "中"
        assert "张三" in content["summary"]

    def test_default_age_fallback(self):
        member = FakeMember("Dave", None, "English")
        provider = RuleBasedProvider()
        content = provider.generate_report_content(member)
        assert content["risk_level"] == "Low"  # defaults to 30

    def test_provider_name(self):
        provider = RuleBasedProvider()
        assert provider.provider_name == "rule_based"

    def test_model_name(self):
        provider = RuleBasedProvider()
        assert provider.model_name == "wellness-os-rules-v1"


class TestOpenAIProvider:
    def test_is_placeholder(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.provider_name == "openai"
        assert provider.model_name == "openai-placeholder-v1"
        with pytest.raises(NotImplementedError):
            provider.generate_report_content(FakeMember("X", 30, "English"))


class TestDeepSeekProvider:
    def test_is_placeholder(self):
        provider = DeepSeekProvider(api_key="sk-test")
        assert provider.provider_name == "deepseek"
        assert provider.model_name == "deepseek-placeholder-v1"
        with pytest.raises(NotImplementedError):
            provider.generate_report_content(FakeMember("X", 30, "English"))


class TestFactory:
    """Tests for the create_ai_provider factory function."""

    def test_default_is_rule_based(self):
        provider = create_ai_provider()
        assert isinstance(provider, RuleBasedProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "rule_based"})
    def test_explicit_rule_based(self):
        provider = create_ai_provider()
        assert isinstance(provider, RuleBasedProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": ""})
    def test_openai_fallback_when_key_missing(self):
        """Should fall back to RuleBasedProvider if OPENAI_API_KEY is empty."""
        provider = create_ai_provider()
        assert isinstance(provider, RuleBasedProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "sk-real-key"})
    def test_openai_with_key(self):
        provider = create_ai_provider()
        assert isinstance(provider, OpenAIProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "deepseek", "DEEPSEEK_API_KEY": ""})
    def test_deepseek_fallback_when_key_missing(self):
        provider = create_ai_provider()
        assert isinstance(provider, RuleBasedProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "deepseek", "DEEPSEEK_API_KEY": "sk-real-key"})
    def test_deepseek_with_key(self):
        provider = create_ai_provider()
        assert isinstance(provider, DeepSeekProvider)

    @patch.dict(os.environ, {"AI_PROVIDER": "unknown_value"})
    def test_unknown_provider_falls_back(self):
        provider = create_ai_provider()
        assert isinstance(provider, RuleBasedProvider)

    def test_env_not_set_still_defaults(self):
        """When AI_PROVIDER is not set at all, should return RuleBasedProvider."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_ai_provider()
            assert isinstance(provider, RuleBasedProvider)


# ── Helpers ────────────────────────────────────────────────────────

class FakeMember:
    """Minimal member-like object for provider unit tests."""
    def __init__(self, name: str, age: int | None, preferred_language: str):
        self.name = name
        self.age = age
        self.preferred_language = preferred_language
