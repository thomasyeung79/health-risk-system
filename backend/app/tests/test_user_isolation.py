"""Tests for user data isolation — verifying users can only see their own data."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.user import User
from app.services.auth import hash_password, create_access_token


HEALTH = {
    "language": "English", "weight_kg": 70.0, "height_cm": 175.0, "water_l": 2.0,
    "situation": "A", "thirst_level": "A", "urine_color": "A",
    "sleep_hours": 7.5, "night_wake_times": 0,
    "difficulty_falling_asleep": "A", "irregular_sleep_schedule": "A",
    "exercise_minutes": 30, "sedentary_hours": 4,
    "fruit_veg_servings": 5, "fast_food_times": 0, "sugary_drinks": 0,
    "screen_time_hours": 3.0,
    "smoking": "A", "alcohol": "A", "late_night": "A",
    "risk_score_emotion": "A", "risk_score_focus": "A", "risk_score_body": "A",
}

EMOTION = {
    "language": "English", "mood_key": "Calm",
    "event_key": "Nothing special", "energy": 7, "stress": 3,
}


@pytest.fixture(scope="function")
def user_b_token(db_session):
    """Create a second test user and return auth headers."""
    user = User(username="user_b", password_hash=hash_password("pass"), display_name="User B")
    db_session.add(user)
    db_session.flush()
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def client_a(db_session, auth_headers):
    """TestClient as user A."""
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c
    app.dependency_overrides.clear()


def _client_b(db_session, headers):
    """Create a TestClient for user B."""
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        c.headers.update(headers)
        return c
    app.dependency_overrides.clear()


class TestHealthIsolation:
    def test_user_b_cannot_see_user_a_health(self, db_session, client_a, user_b_token):
        resp_a = client_a.post("/api/v1/health/check", json=HEALTH)
        record_id = resp_a.json()["id"]

        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            c.headers.update(user_b_token)
            resp_b = c.get(f"/api/v1/health/records/{record_id}")
        assert resp_b.status_code == 404

    def test_user_sees_only_own_records(self, db_session, client_a, user_b_token):
        client_a.post("/api/v1/health/check", json=HEALTH)

        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            c.headers.update(user_b_token)
            resp = c.get("/api/v1/health/records")
        assert resp.json()["total"] == 0


class TestEmotionIsolation:
    def test_user_b_cannot_see_user_a_emotion(self, db_session, client_a, user_b_token):
        resp_a = client_a.post("/api/v1/emotion/analyze", json=EMOTION)
        record_id = resp_a.json()["id"]

        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            c.headers.update(user_b_token)
            resp_b = c.get(f"/api/v1/emotion/records/{record_id}")
        assert resp_b.status_code == 404


class TestReportIsolation:
    def test_user_b_cannot_see_user_a_report(self, db_session, client_a, user_b_token):
        with patch.dict("os.environ", {}, clear=True):
            resp_a = client_a.post("/api/v1/reports/generate",
                json={"language": "English", "style": "balanced", "days": 7})
        record_id = resp_a.json()["id"]

        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            c.headers.update(user_b_token)
            resp_b = c.get(f"/api/v1/reports/{record_id}")
        assert resp_b.status_code == 404


class TestUnauthenticated:
    def test_health_check_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            resp = c.post("/api/v1/health/check", json=HEALTH)
        assert resp.status_code == 401

    def test_emotion_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            resp = c.post("/api/v1/emotion/analyze", json=EMOTION)
        assert resp.status_code == 401

    def test_trend_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            resp = c.get("/api/v1/trends/summary")
        assert resp.status_code == 401
