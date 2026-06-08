"""Wellness report API client."""

from typing import Any, Optional

from api_client.client import ApiClient


class ReportClient:
    """Client for wellness report endpoints."""

    def __init__(self, client: ApiClient):
        self._client = client

    def generate(
        self,
        language: str = "English",
        style: str = "balanced",
        days: int = 7,
    ) -> dict[str, Any]:
        """Generate a wellness report."""
        return self._client.post("/api/v1/reports/generate", json={
            "language": language,
            "style": style,
            "days": days,
        })

    def list_reports(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._client.get("/api/v1/reports", params={
            "limit": limit, "offset": offset,
        })

    def get_report(self, report_id: int) -> dict[str, Any]:
        return self._client.get(f"/api/v1/reports/{report_id}")
