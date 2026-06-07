"""DeepSeek LLM provider — uses OpenAI-compatible SDK."""

import time
from typing import Optional

from openai import OpenAI

from app.services.report_engine.provider import LLMProvider


class DeepSeekProvider(LLMProvider):
    """LLM provider that calls DeepSeek via OpenAI-compatible API."""

    BASE_URL = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        base_url: str = BASE_URL,
        timeout: int = 60,
    ):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._timeout = timeout
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        return "deepseek"

    @property
    def cost_per_1k_tokens(self) -> float:
        return 0.00014  # ~$0.14/M tokens for deepseek-chat

    def model_name(self) -> str:
        return self._model

    def generate(
        self,
        system_prompt: str,
        user_context: str,
    ) -> str:
        """Call DeepSeek and return the response text."""
        start = time.time()

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        self._latency_ms = int((time.time() - start) * 1000)
        self._tokens_used = response.usage.total_tokens if response.usage else 0

        return response.choices[0].message.content or ""

    @property
    def last_tokens_used(self) -> int:
        """Return tokens used in the last generate() call."""
        return getattr(self, "_tokens_used", 0)

    @property
    def last_latency_ms(self) -> int:
        """Return latency in ms from the last generate() call."""
        return getattr(self, "_latency_ms", 0)
