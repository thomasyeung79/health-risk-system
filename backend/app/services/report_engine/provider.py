"""Abstract LLM provider interface and provider factory."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_context: str,
    ) -> str:
        """Send a prompt to the LLM and return the response text."""
        ...

    @abstractmethod
    def model_name(self) -> str:
        """Return the model name string (e.g. 'deepseek-chat')."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g. 'deepseek')."""
        ...

    @property
    @abstractmethod
    def cost_per_1k_tokens(self) -> float:
        """Estimated USD cost per 1K tokens (input + output average)."""
        ...


def create_provider() -> LLMProvider:
    """Create the appropriate provider based on environment configuration.

    Priority:
    1. DeepSeek if DEEPSEEK_API_KEY is set
    2. Local fallback otherwise
    """
    import os

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key and api_key.strip():
        from app.services.report_engine.deepseek_provider import DeepSeekProvider
        return DeepSeekProvider(api_key=api_key.strip())

    from app.services.report_engine.local_provider import LocalProvider
    return LocalProvider()
