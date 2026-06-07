"""Local template-based report provider — zero-cost fallback when no API key is configured."""

from app.services.report_engine.provider import LLMProvider


_LOCAL_TEMPLATES = {
    "English": {
        "high_risk": "Your health readings show elevated risk in several areas. "
        "Consider focusing on recovery, sleep quality, and stress management "
        "as the first priorities. Small, consistent changes are more sustainable "
        "than trying to fix everything at once.",

        "medium_risk": "Your wellness data shows a few areas worth monitoring. "
        "The best approach is to pick one or two habits to adjust this week "
        "rather than making many changes simultaneously.",

        "low_risk": "Your overall wellness indicators are in a good range. "
        "Continue maintaining your current habits and monitor for any changes "
        "in sleep quality or stress levels.",

        "no_data": "Not enough health data to generate a detailed analysis. "
        "Complete at least one health check and one emotion analysis session "
        "to unlock the AI-powered wellness report.",
    },
    "中文": {
        "high_risk": "你的健康数据显示多个指标处于较高风险水平。"
        "建议优先关注恢复、睡眠质量和压力管理。"
        "小幅度但持续的改变比一次性解决所有问题更可持续。",

        "medium_risk": "你的健康数据中有几个指标值得关注。"
        "本周最好选择一两个习惯进行调整，而不是同时改变所有事情。",

        "low_risk": "你的整体健康指标处于良好范围。"
        "请继续保持当前习惯，同时关注睡眠质量和压力水平的变化。",

        "no_data": "没有足够的健康数据来生成详细分析。"
        "请至少完成一次健康检测和一次情绪分析，以解锁 AI 健康报告。",
    },
}

_STYLE_LABELS = {
    "English": {
        "balanced": "Wellness Overview",
        "coaching": "Your Wellness Guide",
        "clinical": "Wellness Assessment",
    },
    "中文": {
        "balanced": "综合健康概览",
        "coaching": "你的健康指南",
        "clinical": "健康评估报告",
    },
}


class LocalProvider(LLMProvider):
    """Template-based report generator. Zero cost, no API calls."""

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def cost_per_1k_tokens(self) -> float:
        return 0.0

    def model_name(self) -> str:
        return "template"

    def generate(
        self,
        system_prompt: str,
        user_context: str,
    ) -> str:
        """Generate a structured report from context without calling any LLM.

        This provider parses the context built by ContextBuilder and produces
        a structured text report. It does NOT call any external API.
        """
        # Parse the context summary to determine risk level
        context = user_context or ""
        lang = "English"
        if "language: 中文" in context or "语言: 中文" in context:
            lang = "中文"

        # Determine risk level from context
        has_data = "health_score" in context or "health_record" in context
        if not has_data:
            return _LOCAL_TEMPLATES[lang]["no_data"]

        # Simple heuristic: look for risk indicators in the context
        is_high_risk = any(
            kw in context.lower() for kw in
            ["score: 3", "high risk", "risk_score: 3", "elevated risk"]
        )
        is_medium_risk = any(
            kw in context.lower() for kw in
            ["score: 2", "medium risk", "risk_score: 2"]
        )

        if is_high_risk:
            content = _LOCAL_TEMPLATES[lang]["high_risk"]
        elif is_medium_risk:
            content = _LOCAL_TEMPLATES[lang]["medium_risk"]
        else:
            content = _LOCAL_TEMPLATES[lang]["low_risk"]

        return content
