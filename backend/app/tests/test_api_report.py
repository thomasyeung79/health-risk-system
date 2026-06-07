"""Integration tests for report API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


SAMPLE_PAYLOAD = {
    "language": "English",
    "style": "balanced",
    "days": 7,
}


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestGenerateReport:
    def test_generate_local(self, client):
        """POST generates a report using local provider (no API key)."""
        with patch.dict("os.environ", {}, clear=True):
            resp = client.post("/api/v1/reports/generate", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "local"
        assert data["is_fallback"] is False
        assert "summary" in data["report"]
        assert "sections" in data["report"]
        assert "token_usage" in data

    def test_generate_chinese(self, client):
        with patch.dict("os.environ", {}, clear=True):
            resp = client.post("/api/v1/reports/generate", json={
                **SAMPLE_PAYLOAD, "language": "中文",
            })
        assert resp.status_code == 200
        assert resp.json()["language"] == "中文"

    def test_cached_on_second_call(self, client):
        with patch.dict("os.environ", {}, clear=True):
            resp1 = client.post("/api/v1/reports/generate", json=SAMPLE_PAYLOAD)
            resp2 = client.post("/api/v1/reports/generate", json=SAMPLE_PAYLOAD)
        assert resp2.json()["is_cached"] is True
        assert resp2.json()["id"] == resp1.json()["id"]

    def test_validation_error(self, client):
        payload = {**SAMPLE_PAYLOAD, "style": "invalid"}
        with patch.dict("os.environ", {}, clear=True):
            resp = client.post("/api/v1/reports/generate", json=payload)
        assert resp.status_code == 422


class TestListReports:
    def test_list_empty(self, client):
        with patch.dict("os.environ", {}, clear=True):
            resp = client.get("/api/v1/reports")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_after_generate(self, client):
        with patch.dict("os.environ", {}, clear=True):
            client.post("/api/v1/reports/generate", json=SAMPLE_PAYLOAD)
            resp = client.get("/api/v1/reports")
        assert resp.json()["total"] == 1

    def test_pagination(self, client):
        styles = ["balanced", "coaching", "clinical"]
        with patch.dict("os.environ", {}, clear=True):
            for style in styles:
                client.post("/api/v1/reports/generate", json={**SAMPLE_PAYLOAD, "style": style})
            resp = client.get("/api/v1/reports?limit=2")
        assert resp.json()["total"] == 3
        assert len(resp.json()["items"]) == 2


class TestGetReport:
    def test_get_existing(self, client):
        with patch.dict("os.environ", {}, clear=True):
            create = client.post("/api/v1/reports/generate", json=SAMPLE_PAYLOAD)
            rid = create.json()["id"]
            resp = client.get(f"/api/v1/reports/{rid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == rid

    def test_get_nonexistent(self, client):
        resp = client.get("/api/v1/reports/9999")
        assert resp.status_code == 404
