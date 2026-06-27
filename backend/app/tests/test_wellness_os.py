"""Integration tests for Wellness OS APIs."""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.member import Member
from app.models.user import User
from app.services.auth import hash_password, create_access_token


MEMBER_PAYLOAD = {"name": "Alice", "gender": "Female", "age": 35, "country": "UK"}


@pytest.fixture(scope="function")
def client(db_session, auth_headers):
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        c.headers.update(auth_headers)
        yield c
    app.dependency_overrides.clear()


class TestMembers:
    def test_create(self, client):
        r = client.post("/api/v1/members", json=MEMBER_PAYLOAD)
        assert r.status_code == 201
        assert r.json()["name"] == "Alice"

    def test_list(self, client):
        client.post("/api/v1/members", json=MEMBER_PAYLOAD)
        r = client.get("/api/v1/members")
        assert r.json()["total"] == 1

    def test_get(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.get(f"/api/v1/members/{m['id']}")
        assert r.status_code == 200

    def test_update(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.patch(f"/api/v1/members/{m['id']}", json={"name": "Alice 2"})
        assert r.json()["name"] == "Alice 2"

    def test_delete(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.delete(f"/api/v1/members/{m['id']}")
        assert r.status_code == 204

    def test_404(self, client):
        assert client.get("/api/v1/members/9999").status_code == 404

    def test_isolation(self, db_session, test_user):
        """User B cannot see user A's members."""
        user_a, _ = test_user
        user_b = User(username="other_user", password_hash=hash_password("x"))
        db_session.add(user_b)
        db_session.flush()

        # Create a member for user A directly
        db_session.add(Member(user_id=user_a.id, name="Alice", age=35))
        db_session.flush()

        # Query as user B
        tok_b = create_access_token(user_b.id)
        def o():
            yield db_session
        app.dependency_overrides[get_db] = o
        with TestClient(app) as c:
            c.headers.update({"Authorization": f"Bearer {tok_b}"})
            assert c.get("/api/v1/members").json()["total"] == 0


class TestConsultations:
    def test_create(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/consultations", json={
            "member_id": m["id"], "consultation_type": "initial",
            "main_concern": "Sleep issues",
        })
        assert r.status_code == 201

    def test_list(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        client.post("/api/v1/consultations", json={"member_id": m["id"]})
        assert client.get("/api/v1/consultations").json()["total"] == 1


class TestAIReports:
    def test_generate(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/ai-reports/generate", json={"member_id": m["id"]})
        assert r.status_code == 201
        assert r.json()["model_used"] == "wellness-os-rules-v1"

    def test_list(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        client.post("/api/v1/ai-reports/generate", json={"member_id": m["id"]})
        assert client.get("/api/v1/ai-reports").json()["total"] == 1


class TestHealingPlans:
    def test_create(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        r = client.post("/api/v1/healing-plans", json={
            "member_id": m["id"], "title": "Sleep Plan",
        })
        assert r.status_code == 201

    def test_update(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        p = client.post("/api/v1/healing-plans", json={
            "member_id": m["id"], "title": "X",
        }).json()
        r = client.patch(f"/api/v1/healing-plans/{p['id']}", json={"status": "completed"})
        assert r.json()["status"] == "completed"


class TestCommunityCases:
    def test_create(self, client):
        r = client.post("/api/v1/community-cases", json={
            "title": "Test Case", "category": "sleep", "is_public": True,
        })
        assert r.status_code == 201


class TestDashboard:
    def test_empty(self, client):
        r = client.get("/api/v1/dashboard/summary")
        assert r.json()["total_members"] == 0

    def test_with_data(self, client):
        m = client.post("/api/v1/members", json=MEMBER_PAYLOAD).json()
        client.post("/api/v1/consultations", json={"member_id": m["id"]})
        d = client.get("/api/v1/dashboard/summary").json()
        assert d["total_members"] == 1
        assert d["total_consultations"] == 1


class TestAuth:
    def test_401(self, db_session):
        def o():
            yield db_session
        app.dependency_overrides[get_db] = o
        with TestClient(app) as c:
            assert c.post("/api/v1/members", json=MEMBER_PAYLOAD).status_code == 401
            assert c.post("/api/v1/consultations", json={"member_id": 1}).status_code == 401
            assert c.post("/api/v1/ai-reports/generate", json={"member_id": 1}).status_code == 401
            assert c.get("/api/v1/dashboard/summary").status_code == 401
