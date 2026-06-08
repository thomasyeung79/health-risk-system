"""Emotion analysis API client."""

from typing import Any, Optional

from api_client.client import ApiClient


class EmotionClient:
    """Client for emotion analysis endpoints."""

    def __init__(self, client: ApiClient):
        self._client = client

    def analyze(
        self,
        language: str = "English",
        mood_key: str = "Calm",
        event_key: str = "Nothing special",
        energy: int = 5,
        stress: int = 5,
    ) -> dict[str, Any]:
        """Run emotion analysis."""
        return self._client.post("/api/v1/emotion/analyze", json={
            "language": language,
            "mood_key": mood_key,
            "event_key": event_key,
            "energy": energy,
            "stress": stress,
        })

    def list_records(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self._client.get("/api/v1/emotion/records", params={
            "limit": limit, "offset": offset,
        })

    def get_record(self, record_id: int) -> dict[str, Any]:
        return self._client.get(f"/api/v1/emotion/records/{record_id}")

    def stats(self) -> dict[str, Any]:
        return self._client.get("/api/v1/emotion/stats")
