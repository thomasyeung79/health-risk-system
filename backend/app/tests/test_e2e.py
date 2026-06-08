"""End-to-end tests verifying full health + emotion API flows."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app

HEALTH_SAMPLE = {
    "language": "English",
    "weight_kg": 70.0, "height_cm": 175.0, "water_l": 2.0,
    "situation": "A", "thirst_level": "A", "urine_color": "A",
    "sleep_hours": 7.5, "night_wake_times": 0,
    "difficulty_falling_asleep": "A", "irregular_sleep_schedule": "A",
    "exercise_minutes": 30, "sedentary_hours": 4,
    "fruit_veg_servings": 5, "fast_food_times": 0, "sugary_drinks": 0,
    "screen_time_hours": 3.0,
    "smoking": "A", "alcohol": "A", "late_night": "A",
    "risk_score_emotion": "A", "risk_score_focus": "A", "risk_score_body": "A",
}

EMOTION_SAMPLE = {
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


class TestHealthE2E:
    """Full health check lifecycle."""

    def test_health_full_flow(self, client):
        # 1. Submit health check
        resp = client.post("/api/v1/health/check", json=HEALTH_SAMPLE)
        assert resp.status_code == 200
        result = resp.json()
        assert result["health_score"] == 100.0
        assert result["id"] == 1

        # 2. List records
        resp = client.get("/api/v1/health/records")
        assert resp.status_code == 200
        list_data = resp.json()
        assert list_data["total"] == 1
        assert len(list_data["items"]) == 1

        # 3. Get single record
        resp = client.get(f"/api/v1/health/records/{result['id']}")
        assert resp.status_code == 200
        assert resp.json()["health_score"] == 100.0

        # 4. Get stats
        resp = client.get("/api/v1/health/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_records"] == 1
        assert stats["average_health_score"] == 100.0
        assert stats["latest_risk_level"] == "Healthy"


class TestEmotionE2E:
    """Full emotion analysis lifecycle."""

    def test_emotion_full_flow(self, client):
        # 1. Submit emotion analysis
        resp = client.post("/api/v1/emotion/analyze", json=EMOTION_SAMPLE)
        assert resp.status_code == 200
        result = resp.json()
        assert result["id"] == 1
        assert result["matched_topic"] is not None
        assert len(result["full_story"]) > 50

        # 2. List records
        resp = client.get("/api/v1/emotion/records")
        assert resp.status_code == 200
        list_data = resp.json()
        assert list_data["total"] == 1
        assert len(list_data["items"]) == 1

        # 3. Get single record
        resp = client.get(f"/api/v1/emotion/records/{result['id']}")
        assert resp.status_code == 200
        assert resp.json()["pattern_severity"] == "Low"

        # 4. Get stats
        resp = client.get("/api/v1/emotion/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_records"] == 1
        assert stats["latest_mood"] == "Calm"


class TestModulesCoexist:
    """Verify both modules work together."""

    def test_both_modules_on_same_db(self, client):
        # Run health check
        client.post("/api/v1/health/check", json=HEALTH_SAMPLE)
        # Run emotion analysis
        client.post("/api/v1/emotion/analyze", json=EMOTION_SAMPLE)

        # Both tables have records
        health_stats = client.get("/api/v1/health/stats").json()
        emotion_stats = client.get("/api/v1/emotion/stats").json()

        assert health_stats["total_records"] == 1
        assert emotion_stats["total_records"] == 1

    def test_multiple_records_pagination(self, client):
        """Insert multiple records and test pagination."""
        for _ in range(3):
            client.post("/api/v1/health/check", json=HEALTH_SAMPLE)
            client.post("/api/v1/emotion/analyze", json=EMOTION_SAMPLE)

        health_resp = client.get("/api/v1/health/records?limit=2")
        assert health_resp.json()["total"] == 3
        assert len(health_resp.json()["items"]) == 2

        emotion_resp = client.get("/api/v1/emotion/records?limit=2")
        assert emotion_resp.json()["total"] == 3
        assert len(emotion_resp.json()["items"]) == 2

    def test_record_not_found(self, client):
        """Both endpoints return 404 for non-existent records."""
        assert client.get("/api/v1/health/records/9999").status_code == 404
        assert client.get("/api/v1/emotion/records/9999").status_code == 404
