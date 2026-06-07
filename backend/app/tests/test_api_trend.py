"""Integration tests for trend analysis API."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.health_record import HealthRecord
from app.models.emotion_record import EmotionRecord


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestTrendSummary:
    def test_empty_db(self, client):
        """Returns valid structure even without data."""
        resp = client.get("/api/v1/trends/summary?days=7")
        assert resp.status_code == 200
        data = resp.json()
        assert data["days_analyzed"] == 7
        assert data["health_data_points"] == 0
        assert data["emotion_data_points"] == 0
        assert data["overall_direction"] == "insufficient_data"
        assert len(data["metrics"]) == 4

    def test_with_health_data(self, client, db_session):
        dt = datetime.utcnow() - timedelta(days=5)
        db_session.add(HealthRecord(created_at=dt, language="English", health_score=75.0, sleep_score=2))
        db_session.add(HealthRecord(language="English", health_score=85.0, sleep_score=1))
        db_session.flush()

        resp = client.get("/api/v1/trends/summary?days=7")
        assert resp.status_code == 200
        data = resp.json()
        assert data["health_data_points"] == 2
        assert data["metrics"][0]["metric"] == "health_score"
        assert data["metrics"][0]["direction"] in ("improving", "stable", "declining")

    def test_with_emotion_data(self, client, db_session):
        dt = datetime.utcnow() - timedelta(days=3)
        db_session.add(EmotionRecord(created_at=dt, language="English", stress=7, energy=4))
        db_session.add(EmotionRecord(language="English", stress=4, energy=6))
        db_session.flush()

        resp = client.get("/api/v1/trends/summary?days=7")
        assert resp.status_code == 200
        data = resp.json()
        assert data["emotion_data_points"] == 2
        assert data["metrics"][2]["metric"] == "energy"
        assert data["metrics"][2]["direction"] == "improving"

    def test_with_language_param(self, client, db_session):
        db_session.add(HealthRecord(language="中文", health_score=80.0, sleep_score=1))
        db_session.add(HealthRecord(language="中文", health_score=85.0, sleep_score=0))
        db_session.flush()

        resp = client.get("/api/v1/trends/summary?days=7&language=English")
        assert resp.status_code == 200
        assert resp.json()["health_data_points"] == 2

    def test_custom_days(self, client):
        resp = client.get("/api/v1/trends/summary?days=30")
        assert resp.status_code == 200
        assert resp.json()["days_analyzed"] == 30

    def test_invalid_days(self, client):
        resp = client.get("/api/v1/trends/summary?days=0")
        assert resp.status_code == 422
