"""Health check API client."""

from typing import Any, Optional

from api_client.client import ApiClient


class HealthClient:
    """Client for health check endpoints."""

    def __init__(self, client: ApiClient):
        self._client = client

    def check(self, **inputs: Any) -> dict[str, Any]:
        """Run a full health assessment."""
        return self._client.post("/api/v1/health/check", json=inputs)

    def list_records(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List health records with pagination."""
        return self._client.get("/api/v1/health/records", params={
            "limit": limit, "offset": offset,
        })

    def get_record(self, record_id: int) -> dict[str, Any]:
        """Get a single health record by ID."""
        return self._client.get(f"/api/v1/health/records/{record_id}")

    def stats(self) -> dict[str, Any]:
        """Get aggregated health statistics."""
        return self._client.get("/api/v1/health/stats")
