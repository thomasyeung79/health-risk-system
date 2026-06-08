"""Integration tests for authentication API."""

from fastapi.testclient import TestClient
import pytest

from app.database import get_db
from app.main import app


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


REGISTER_PAYLOAD = {
    "username": "testuser",
    "password": "securePass123",
    "display_name": "Test User",
    "preferred_language": "English",
}


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["display_name"] == "Test User"
        assert data["preferred_language"] == "English"
        assert "id" in data
        assert "password_hash" not in data

    def test_register_duplicate(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 409

    def test_register_short_password(self, client):
        payload = {**REGISTER_PAYLOAD, "password": "ab"}
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422

    def test_register_chinese(self, client):
        payload = {**REGISTER_PAYLOAD, "username": "chinese_user", "preferred_language": "中文"}
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        assert resp.json()["preferred_language"] == "中文"


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "securePass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_nonexistent(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "nobody", "password": "x",
        })
        assert resp.status_code == 401


class TestRefresh:
    def test_refresh_success(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        login = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "securePass123",
        }).json()
        rt = login["refresh_token"]

        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["refresh_token"] != rt

    def test_refresh_revoked(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        login = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "securePass123",
        }).json()
        rt = login["refresh_token"]

        client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        assert resp.status_code == 401

    def test_refresh_invalid(self, client):
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "x" * 20})
        assert resp.status_code == 401


class TestLogout:
    def test_logout_then_refresh_fails(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        login = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "securePass123",
        }).json()
        rt = login["refresh_token"]

        client.post("/api/v1/auth/logout", json={"refresh_token": rt})
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client):
        client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
        login = client.post("/api/v1/auth/login", json={
            "username": "testuser", "password": "securePass123",
        }).json()
        at = login["access_token"]

        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {at}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_me_no_token(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad"})
        assert resp.status_code == 401
