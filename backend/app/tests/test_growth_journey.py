"""Tests for Growth Journey — generation, list, detail, and user isolation."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.user import User
from app.services.auth import hash_password, create_access_token


MEMBER_PAYLOAD = {"name": "Alice Growth", "gender": "Female", "age": 35, "country": "UK"}


@pytest.fixture(scope="function")
def client(db_session, auth_headers):
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c
    app.dependency_overrides.clear()


class TestGrowthJourneyGenerate:
    def test_generate(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]})
        assert r.status_code == 201
        data = r.json()
        assert data["title"]
        assert data["summary"]
        assert "timeline_items" in data
        assert "insights" in data

    def test_generate_member_not_found(self, client):
        r = client.post("/api/v1/growth-journeys/generate", json={"member_id": 9999})
        assert r.status_code == 404

    def test_generate_insights_fields(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]})
        insights = r.json()["insights"]
        assert "emotional_pattern" in insights
        assert "key_challenges" in insights
        assert "healing_actions" in insights
        assert "progress_summary" in insights
        assert "next_step_suggestions" in insights

    def test_generate_timeline_has_member_created_event(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]})
        timeline = r.json()["timeline_items"]
        types = [e["event_type"] for e in timeline]
        assert "member_created" in types

    def test_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            r = c.post("/api/v1/growth-journeys/generate", json={"member_id": 1})
        assert r.status_code == 401


class TestGrowthJourneyList:
    def test_list_empty(self, client):
        r = client.get("/api/v1/growth-journeys")
        assert r.json()["total"] == 0

    def test_list_after_generate(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        client.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]})
        r = client.get("/api/v1/growth-journeys")
        assert r.json()["total"] == 1

    def test_list_filter_by_member(self, client):
        m1 = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        m2 = client.post("/api/v1/members", json={"name": "Bob Growth", "age": 40}).json()
        client.post("/api/v1/growth-journeys/generate", json={"member_id": m1["id"]})
        client.post("/api/v1/growth-journeys/generate", json={"member_id": m2["id"]})
        # Filter by m1
        r = client.get(f"/api/v1/growth-journeys?member_id={m1['id']}")
        assert r.json()["total"] == 1
        items = r.json()["items"]
        assert all(i["member_id"] == m1["id"] for i in items)


class TestGrowthJourneyDetail:
    def test_get_journey(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        j = client.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]}).json()
        r = client.get(f"/api/v1/growth-journeys/{j['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == j["id"]

    def test_get_404(self, client):
        r = client.get("/api/v1/growth-journeys/9999")
        assert r.status_code == 404

    def test_get_requires_auth(self, db_session):
        def override():
            yield db_session
        app.dependency_overrides[get_db] = override
        with TestClient(app) as c:
            r = c.get("/api/v1/growth-journeys/1")
        assert r.status_code == 401


class TestGrowthJourneyIsolation:
    """User B should not see User A's growth journeys."""

    @pytest.fixture(scope="function")
    def user_b_token(self, db_session):
        user = User(username="other_gj", password_hash=hash_password("pass"), display_name="Other GJ")
        db_session.add(user)
        db_session.flush()
        token = create_access_token(user.id)
        return {"Authorization": f"Bearer {token}"}

    def test_isolation(self, db_session, auth_headers, user_b_token):
        """User B's list should exclude User A's journey."""
        def oa():
            yield db_session
        app.dependency_overrides[get_db] = oa
        with TestClient(app) as c_a:
            c_a.headers.update(auth_headers)
            m = c_a.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
            c_a.post("/api/v1/growth-journeys/generate", json={"member_id": m["id"]})

        def ob():
            yield db_session
        app.dependency_overrides[get_db] = ob
        with TestClient(app) as c_b:
            c_b.headers.update(user_b_token)
            r = c_b.get("/api/v1/growth-journeys")
        assert r.json()["total"] == 0
        app.dependency_overrides.clear()
