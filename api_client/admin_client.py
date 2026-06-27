"""Wellness OS Admin API client."""

from typing import Any, Optional

from api_client.client import ApiClient


class AdminClient:
    """Client for Wellness OS admin endpoints."""

    def __init__(self, client: ApiClient):
        self._client = client

    # ── Dashboard ────────────────────────────────────
    def dashboard_summary(self) -> dict[str, Any]:
        return self._client.get("/api/v1/dashboard/summary")

    # ── Members ──────────────────────────────────────
    def list_members(self, limit=50, offset=0) -> dict[str, Any]:
        return self._client.get("/api/v1/members", params={"limit": limit, "offset": offset})

    def get_member(self, member_id: int) -> dict[str, Any]:
        return self._client.get(f"/api/v1/members/{member_id}")

    def create_member(self, **data) -> dict[str, Any]:
        return self._client.post("/api/v1/members", json=data)

    def update_member(self, member_id: int, **data) -> dict[str, Any]:
        return self._client.patch(f"/api/v1/members/{member_id}", json=data)

    def delete_member(self, member_id: int) -> None:
        self._client.delete(f"/api/v1/members/{member_id}")

    # ── Consultations ────────────────────────────────
    def list_consultations(self, limit=50, offset=0) -> dict[str, Any]:
        return self._client.get("/api/v1/consultations", params={"limit": limit, "offset": offset})

    def get_consultation(self, cid: int) -> dict[str, Any]:
        return self._client.get(f"/api/v1/consultations/{cid}")

    def create_consultation(self, **data) -> dict[str, Any]:
        return self._client.post("/api/v1/consultations", json=data)

    # ── AI Reports ───────────────────────────────────
    def list_ai_reports(self, limit=50, offset=0) -> dict[str, Any]:
        return self._client.get("/api/v1/ai-reports", params={"limit": limit, "offset": offset})

    def generate_ai_report(self, member_id: int, consultation_id: Optional[int] = None) -> dict[str, Any]:
        body = {"member_id": member_id}
        if consultation_id:
            body["consultation_id"] = consultation_id
        return self._client.post("/api/v1/ai-reports/generate", json=body)

    # ── Healing Plans ────────────────────────────────
    def list_healing_plans(self, limit=50, offset=0) -> dict[str, Any]:
        return self._client.get("/api/v1/healing-plans", params={"limit": limit, "offset": offset})

    def create_healing_plan(self, **data) -> dict[str, Any]:
        return self._client.post("/api/v1/healing-plans", json=data)

    def update_healing_plan(self, plan_id: int, **data) -> dict[str, Any]:
        return self._client.patch(f"/api/v1/healing-plans/{plan_id}", json=data)

    # ── Community Cases ──────────────────────────────
    def list_community_cases(self, limit=50, offset=0, public_only: bool = True) -> dict[str, Any]:
        return self._client.get(
            "/api/v1/community-cases",
            params={"limit": limit, "offset": offset, "public_only": public_only},
        )

    def get_community_case(self, case_id: int) -> dict[str, Any]:
        return self._client.get(f"/api/v1/community-cases/{case_id}")

    def create_community_case(self, **data) -> dict[str, Any]:
        return self._client.post("/api/v1/community-cases", json=data)
