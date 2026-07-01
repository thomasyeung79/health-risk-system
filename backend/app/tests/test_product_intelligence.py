"""Tests for Pattern Discovery Engine, Insights Dashboard, AI Coach, and Daily Reflections."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.user import User
from app.services.auth import hash_password, create_access_token


MEMBER_PAYLOAD = {"name": "Insight User", "gender": "Female", "age": 35, "country": "UK"}
HEALTH_PAYLOAD = {
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
EMOTION_PAYLOAD = {
    "language": "English", "mood_key": "Calm",
    "event_key": "Nothing special", "energy": 8, "stress": 3,
}


@pytest.fixture(scope="function")
def client(db_session, auth_headers):
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c
    app.dependency_overrides.clear()


# ── Helper ──────────────────────────────────────────────────────────

def create_member(client):
    return client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()


def add_health_data(client, db_session):
    from app.models.health_record import HealthRecord
    import datetime
    now = datetime.datetime.utcnow()
    for i in range(3):
        hr = HealthRecord(
            user_id=1, language="English", weight_kg=70.0, height_cm=175.0,
            sleep_hours=7.5, exercise_minutes=30, fruit_veg_servings=5,
            fast_food_times=0, sugary_drinks=0, health_score=75.0 + i * 5,
            risk_level="Low", overall="Good", primary_focus="Sleep",
            action_plan="Keep it up",
            created_at=now - datetime.timedelta(days=i * 7),
        )
        db_session.add(hr)
    db_session.flush()


def add_emotion_data(client, db_session):
    from app.models.emotion_record import EmotionRecord
    import datetime
    now = datetime.datetime.utcnow()
    for i in range(3):
        er = EmotionRecord(
            user_id=1, language="English", mood_key="Calm",
            event_key="Routine", energy=7, stress=3,
            pattern_key="stable", summary="Feeling good",
            created_at=now - datetime.timedelta(days=i * 3),
        )
        db_session.add(er)
    db_session.flush()


# ══════════════════════════════════════════════════════════════════
# PATTERN DISCOVERY
# ══════════════════════════════════════════════════════════════════

class TestPatternDiscovery:
    def test_get_patterns_empty(self, client):
        m = create_member(client)
        r = client.get(f"/api/v1/patterns/{m['id']}")
        assert r.status_code == 200
        data = r.json()
        assert "patterns" in data
        assert data["member_id"] == m["id"]

    def test_get_patterns_with_data(self, client, db_session):
        m = create_member(client)
        add_health_data(client, db_session)
        add_emotion_data(client, db_session)
        r = client.get(f"/api/v1/patterns/{m['id']}")
        assert r.status_code == 200
        patterns = r.json()["patterns"]
        assert len(patterns) >= 1
        for p in patterns:
            assert "title" in p
            assert "confidence" in p
            assert "evidence" in p
            assert "recommendation" in p

    def test_get_patterns_404(self, client):
        r = client.get("/api/v1/patterns/9999")
        assert r.status_code == 404

    def test_get_patterns_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            r = c.get("/api/v1/patterns/1")
        assert r.status_code == 401


# ══════════════════════════════════════════════════════════════════
# INSIGHTS DASHBOARD
# ══════════════════════════════════════════════════════════════════

class TestInsights:
    def test_get_insights_empty(self, client):
        m = create_member(client)
        r = client.get(f"/api/v1/insights/{m['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["member_id"] == m["id"]
        assert "positive_changes" in data
        assert "risk_alerts" in data
        assert "recent_achievements" in data

    def test_get_insights_with_data(self, client, db_session):
        m = create_member(client)
        add_health_data(client, db_session)
        add_emotion_data(client, db_session)
        r = client.get(f"/api/v1/insights/{m['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["wellness_score"] is not None
        assert data["monthly_trend"]

    def test_get_insights_404(self, client):
        r = client.get("/api/v1/insights/9999")
        assert r.status_code == 404

    def test_get_insights_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            r = c.get("/api/v1/insights/1")
        assert r.status_code == 401


# ══════════════════════════════════════════════════════════════════
# AI COACH
# ══════════════════════════════════════════════════════════════════

class TestAICoach:
    def test_get_daily_message(self, client):
        m = create_member(client)
        r = client.get(f"/api/v1/coach/daily/{m['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["member_id"] == m["id"]
        assert data["title"]
        assert data["content"]
        assert data["message_type"] == "daily_coaching"
        assert data["date"]

    def test_daily_message_is_deterministic(self, client):
        """Same member on same date gets same message (seeded RNG)."""
        m = create_member(client)
        r1 = client.get(f"/api/v1/coach/daily/{m['id']}")
        r2 = client.get(f"/api/v1/coach/daily/{m['id']}")
        assert r1.json()["content"] == r2.json()["content"]

    def test_get_daily_message_404(self, client):
        r = client.get("/api/v1/coach/daily/9999")
        assert r.status_code == 404

    def test_get_daily_message_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            r = c.get("/api/v1/coach/daily/1")
        assert r.status_code == 401


# ══════════════════════════════════════════════════════════════════
# DAILY REFLECTIONS
# ══════════════════════════════════════════════════════════════════

class TestReflections:
    def test_create_reflection(self, client):
        m = create_member(client)
        r = client.post("/api/v1/reflections", json={
            "member_id": m["id"],
            "went_well": "Finished a project",
            "biggest_challenge": "Woke up late",
            "gratitude": "Supportive team",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["member_id"] == m["id"]
        assert data["went_well"] == "Finished a project"
        assert data["gratitude"] == "Supportive team"

    def test_create_reflection_minimal(self, client):
        m = create_member(client)
        r = client.post("/api/v1/reflections", json={
            "member_id": m["id"],
            "notes": "Just a quick note",
        })
        assert r.status_code == 201
        assert r.json()["notes"] == "Just a quick note"

    def test_create_reflection_404(self, client):
        r = client.post("/api/v1/reflections", json={"member_id": 9999})
        assert r.status_code == 404

    def test_list_empty(self, client):
        r = client.get("/api/v1/reflections")
        assert r.json()["total"] == 0

    def test_list_after_create(self, client):
        m = create_member(client)
        client.post("/api/v1/reflections", json={
            "member_id": m["id"], "went_well": "Good day",
        })
        r = client.get("/api/v1/reflections")
        assert r.json()["total"] == 1

    def test_list_filter_by_member(self, client):
        m1 = create_member(client)
        m2 = client.post("/api/v1/members", json={"name": "Bob", "age": 40}).json()
        client.post("/api/v1/reflections", json={"member_id": m1["id"]})
        client.post("/api/v1/reflections", json={"member_id": m2["id"]})
        r = client.get(f"/api/v1/reflections?member_id={m1['id']}")
        assert r.json()["total"] == 1

    def test_weekly_summary(self, client, db_session):
        m = create_member(client)
        now = __import__("datetime").datetime.utcnow()
        from app.models.daily_reflection import DailyReflection
        for i in range(3):
            db_session.add(DailyReflection(
                user_id=1, member_id=m["id"],
                went_well=f"Good thing {i}",
                biggest_challenge="Focus",
                gratitude="Health",
                created_at=now - __import__("datetime").timedelta(days=i),
            ))
        db_session.flush()
        r = client.get(f"/api/v1/reflections/weekly-summary/{m['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["reflection_count"] == 3
        assert data["overall_theme"]
        assert data["suggestion"]

    def test_weekly_summary_404(self, client):
        r = client.get("/api/v1/reflections/weekly-summary/9999")
        assert r.status_code == 404

    def test_reflection_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            assert c.post("/api/v1/reflections", json={"member_id": 1}).status_code == 401
            assert c.get("/api/v1/reflections").status_code == 401
            assert c.get("/api/v1/reflections/weekly-summary/1").status_code == 401
