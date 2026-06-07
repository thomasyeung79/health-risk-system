"""Integration tests for health check API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


SAMPLE_PAYLOAD = {
    "language": "English",
    "weight_kg": 70.0,
    "height_cm": 175.0,
    "water_l": 2.0,
    "situation": "A",
    "thirst_level": "A",
    "urine_color": "A",
    "sleep_hours": 7.5,
    "night_wake_times": 0,
    "difficulty_falling_asleep": "A",
    "irregular_sleep_schedule": "A",
    "exercise_minutes": 30,
    "sedentary_hours": 4,
    "fruit_veg_servings": 5,
    "fast_food_times": 0,
    "sugary_drinks": 0,
    "screen_time_hours": 3.0,
    "smoking": "A",
    "alcohol": "A",
    "late_night": "A",
    "risk_score_emotion": "A",
    "risk_score_focus": "A",
    "risk_score_body": "A",
}


@pytest.fixture(scope="function")
def client(db_session):
    """Create a TestClient that uses the test DB session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    def test_health_check_endpoint(self, client):
        """GET /health should return status ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestPostHealthCheck:
    def test_full_health_check(self, client):
        """POST /api/v1/health/check should return full results."""
        resp = client.post("/api/v1/health/check", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()

        assert data["health_score"] == 100.0
        assert data["risk_percent"] == 0.0
        assert data["risk_level"] == "Healthy"
        assert data["language"] == "English"
        assert data["id"] == 1

        # Verify all 8 modules present
        assert set(data["modules"].keys()) == {
            "BMI", "Water", "Sleep", "Activity",
            "Diet", "Mental", "Screen", "Habit",
        }
        for m in data["modules"].values():
            assert "score" in m
            assert "level" in m
            assert "reasons" in m
            assert "suggestions" in m

    def test_chinese_language(self, client):
        """POST with Chinese language should return Chinese labels."""
        payload = {**SAMPLE_PAYLOAD, "language": "中文"}
        resp = client.post("/api/v1/health/check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] == "健康"
        assert data["health_score"] == 100.0

    def test_high_risk_inputs(self, client):
        """High-risk inputs should produce high risk level."""
        payload = {
            **SAMPLE_PAYLOAD,
            "sleep_hours": 3.0,
            "night_wake_times": 6,
            "difficulty_falling_asleep": "C",
            "irregular_sleep_schedule": "C",
            "exercise_minutes": 0,
            "sedentary_hours": 14,
            "smoking": "C",
            "alcohol": "C",
            "late_night": "C",
            "risk_score_emotion": "C",
            "risk_score_focus": "C",
            "risk_score_body": "C",
        }
        resp = client.post("/api/v1/health/check", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_level"] in ("Medium Risk", "High Risk")
        assert data["health_score"] < 80

    def test_validation_error(self, client):
        """Invalid input should return 422."""
        payload = {**SAMPLE_PAYLOAD, "weight_kg": -1}
        resp = client.post("/api/v1/health/check", json=payload)
        assert resp.status_code == 422


class TestListRecords:
    def test_list_records_empty(self, client):
        """Initially no records should exist."""
        resp = client.get("/api/v1/health/records")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_records_after_insert(self, client):
        """After inserting a record, it should appear in the list."""
        client.post("/api/v1/health/check", json=SAMPLE_PAYLOAD)

        resp = client.get("/api/v1/health/records")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["health_score"] == 100.0

    def test_pagination(self, client):
        """Insert 3 records, verify limit and offset."""
        for _ in range(3):
            client.post("/api/v1/health/check", json=SAMPLE_PAYLOAD)

        resp = client.get("/api/v1/health/records?limit=2&offset=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2


class TestGetRecord:
    def test_get_existing_record(self, client):
        """GET by ID should return the record."""
        create_resp = client.post("/api/v1/health/check", json=SAMPLE_PAYLOAD)
        record_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/health/records/{record_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == record_id
        assert data["weight_kg"] == 70.0
        assert data["health_score"] == 100.0

    def test_get_nonexistent_record(self, client):
        """GET by non-existent ID should return 404."""
        resp = client.get("/api/v1/health/records/9999")
        assert resp.status_code == 404


class TestStats:
    def test_stats_empty(self, client):
        """Stats on empty database."""
        resp = client.get("/api/v1/health/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_records"] == 0
        assert data["average_health_score"] is None
        assert data["latest_risk_level"] is None

    def test_stats_after_records(self, client):
        """Stats after inserting records."""
        client.post("/api/v1/health/check", json=SAMPLE_PAYLOAD)
        resp = client.get("/api/v1/health/stats")
        data = resp.json()
        assert data["total_records"] == 1
        assert data["average_health_score"] == 100.0
        assert data["latest_risk_level"] == "Healthy"
