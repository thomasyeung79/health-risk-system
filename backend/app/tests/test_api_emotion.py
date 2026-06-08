"""Integration tests for emotion analysis API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


SAMPLE_PAYLOAD = {
    "language": "English",
    "mood_key": "Calm",
    "event_key": "Nothing special",
    "energy": 7,
    "stress": 3,
}


@pytest.fixture(scope="function")
def client(db_session, auth_headers):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c
    app.dependency_overrides.clear()


class TestPostAnalyze:
    def test_full_analyze(self, client):
        resp = client.post("/api/v1/emotion/analyze", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["language"] == "English"
        assert "summary" in data
        assert "pattern" in data
        assert "matched_topic" in data
        assert "guidance" in data
        assert "breathing" in data
        assert "full_story" in data
        assert len(data["full_story"]) > 50

    def test_chinese_language(self, client):
        payload = {**SAMPLE_PAYLOAD, "language": "中文"}
        resp = client.post("/api/v1/emotion/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["pattern"]["severity"] == "低"

    def test_validation_error(self, client):
        payload = {**SAMPLE_PAYLOAD, "energy": 0}
        resp = client.post("/api/v1/emotion/analyze", json=payload)
        assert resp.status_code == 422

    def test_invalid_mood(self, client):
        payload = {**SAMPLE_PAYLOAD, "mood_key": "Invalid"}
        resp = client.post("/api/v1/emotion/analyze", json=payload)
        assert resp.status_code == 422


class TestListRecords:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/emotion/records")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_after_insert(self, client):
        client.post("/api/v1/emotion/analyze", json=SAMPLE_PAYLOAD)
        resp = client.get("/api/v1/emotion/records")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1


class TestGetRecord:
    def test_get_existing(self, client):
        create_resp = client.post("/api/v1/emotion/analyze", json=SAMPLE_PAYLOAD)
        record_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/emotion/records/{record_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == record_id

    def test_get_nonexistent(self, client):
        resp = client.get("/api/v1/emotion/records/9999")
        assert resp.status_code == 404


class TestStats:
    def test_stats_empty(self, client):
        resp = client.get("/api/v1/emotion/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_records"] == 0

    def test_stats_after_insert(self, client):
        client.post("/api/v1/emotion/analyze", json=SAMPLE_PAYLOAD)
        resp = client.get("/api/v1/emotion/stats")
        data = resp.json()
        assert data["total_records"] == 1
        assert data["latest_mood"] == "Calm"

