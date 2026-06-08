"""Trend analysis API client."""

from typing import Any

from api_client.client import ApiClient


class TrendClient:
    """Client for trend analysis endpoints."""

    def __init__(self, client: ApiClient):
        self._client = client

    def summary(
        self,
        days: int = 7,
        language: str = "English",
    ) -> dict[str, Any]:
        """Get trend summary for core metrics."""
        return self._client.get("/api/v1/trends/summary", params={
            "days": days,
            "language": language,
        })
