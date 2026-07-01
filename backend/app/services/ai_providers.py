"""Pluggable AI provider layer for Wellness OS report generation.

Supports RuleBasedProvider (default fallback), OpenAIProvider (placeholder),
and DeepSeekProvider (placeholder). Provider selection is driven by the
AI_PROVIDER environment variable. Missing API keys cause safe fallback to
rule_based.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional


# ── Abstract interface ──────────────────────────────────────────────

class AIProvider(ABC):
    """Abstract interface for all AI report providers."""

    @abstractmethod
    def generate_report_content(self, member: Any) -> dict[str, Any]:
        """Generate report content given a member ORM object.

        Returns a dict with keys:
          - summary (str)
          - risk_level (str)
          - key_findings (list[str])
          - recommendations (list[str])
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier, e.g. 'rule_based'."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier string, e.g. 'wellness-os-rules-v1'."""


# ── Rule-based provider (default) ───────────────────────────────────

class RuleBasedProvider(AIProvider):
    """Deterministic, rule-based report generator — no external API calls."""

    def generate_report_content(self, member: Any) -> dict[str, Any]:
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

        return {
            "summary": summary,
            "risk_level": risk_level,
            "key_findings": findings,
            "recommendations": recommendations,
        }

    @property
    def provider_name(self) -> str:
        return "rule_based"

    @property
    def model_name(self) -> str:
        return "wellness-os-rules-v1"


# ── OpenAI provider (placeholder) ───────────────────────────────────

class OpenAIProvider(AIProvider):
    """OpenAI provider — placeholder for future integration."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def generate_report_content(self, member: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "OpenAI provider is a placeholder — no real implementation yet."
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "openai-placeholder-v1"


# ── DeepSeek provider (placeholder) ─────────────────────────────────

class DeepSeekProvider(AIProvider):
    """DeepSeek provider — placeholder for future integration."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def generate_report_content(self, member: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "DeepSeek provider is a placeholder — no real implementation yet."
        )

    @property
    def provider_name(self) -> str:
        return "deepseek"

    @property
    def model_name(self) -> str:
        return "deepseek-placeholder-v1"


# ── Factory ─────────────────────────────────────────────────────────

def create_ai_provider() -> AIProvider:
    """Create the appropriate AI provider based on environment config.

    Selection priority:
      1. AI_PROVIDER=openai   → OpenAIProvider (if OPENAI_API_KEY set)
      2. AI_PROVIDER=deepseek → DeepSeekProvider (if DEEPSEEK_API_KEY set)
      3. AI_PROVIDER=rule_based or any other value → RuleBasedProvider

    If the chosen provider's API key is missing or empty, falls back safely
    to RuleBasedProvider.
    """
    provider_choice = os.environ.get("AI_PROVIDER", "rule_based").strip().lower()

    if provider_choice == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if api_key:
            return OpenAIProvider(api_key=api_key)

    elif provider_choice == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if api_key:
            return DeepSeekProvider(api_key=api_key)

    # Default fallback
    return RuleBasedProvider()
