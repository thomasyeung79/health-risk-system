"""Tests for the API client layer."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from api_client.client import ApiClient, ApiError
from api_client.auth_client import AuthClient
from api_client.health_client import HealthClient
from api_client.emotion_client import EmotionClient
from api_client.report_client import ReportClient
from api_client.trend_client import TrendClient


def _mock_response(status_code=200, json_data=None):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = str(json_data or {})
    return resp


class TestApiClient:
    def test_init_default_url(self):
        c = ApiClient()
        assert c.base_url == "http://localhost:8000"

    def test_init_custom_url(self):
        c = ApiClient("http://api:9000")
        assert c.base_url == "http://api:9000"

    def test_token_management(self):
        c = ApiClient()
        assert c.is_authenticated is False
        c.set_tokens("a", "b")
        assert c.access_token == "a"
        assert c.refresh_token == "b"
        assert c.is_authenticated is True
        c.clear_tokens()
        assert c.is_authenticated is False

    def test_auth_header(self):
        c = ApiClient()
        c.set_tokens("tok", "ref")
        assert c._build_headers()["Authorization"] == "Bearer tok"

    def test_no_auth_header(self):
        c = ApiClient()
        assert "Authorization" not in c._build_headers()


class TestApiClientRequest:
    def test_get(self):
        c = ApiClient()
        with patch.object(c._session, "request", return_value=_mock_response(200, {"k": "v"})):
            assert c.get("/test") == {"k": "v"}

    def test_post(self):
        c = ApiClient()
        with patch.object(c._session, "request", return_value=_mock_response(201, {"id": 1})):
            assert c.post("/test", json={"a": 1}) == {"id": 1}

    def test_404_raises(self):
        c = ApiClient()
        with patch.object(c._session, "request", return_value=_mock_response(404, {"detail": "Not found"})):
            with pytest.raises(ApiError) as e:
                c.get("/missing")
            assert e.value.status_code == 404

    def test_auto_refresh(self):
        c = ApiClient()
        c.set_tokens("old", "old_ref")

        refresh_resp = _mock_response(200, {"access_token": "new", "refresh_token": "new_ref"})
        success = _mock_response(200, {"data": "ok"})

        with patch.object(c._session, "request") as mock_req:
            mock_req.side_effect = [
                _mock_response(401),
                refresh_resp,
                success,
            ]
            result = c.get("/protected")
        assert result == {"data": "ok"}
        assert c.access_token == "new"

    def test_auto_refresh_fails(self):
        c = ApiClient()
        c.set_tokens("old", "old_ref")

        with patch.object(c._session, "request") as mock_req:
            mock_req.side_effect = [
                _mock_response(401),
                _mock_response(401),
            ]
            with pytest.raises(ApiError):
                c.get("/protected")
        assert c.is_authenticated is False


class TestAuthClient:
    def test_register(self):
        c = ApiClient()
        a = AuthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(201, {"username": "t"})):
            assert a.register("t", "p")["username"] == "t"

    def test_login_sets_tokens(self):
        c = ApiClient()
        a = AuthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {
            "access_token": "at", "refresh_token": "rt", "user": {"id": 1},
        })):
            r = a.login("t", "p")
        assert r["user"]["id"] == 1
        assert c.access_token == "at"

    def test_logout_clears_tokens(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        a = AuthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"message": "ok"})):
            a.logout()
        assert c.is_authenticated is False

    def test_me(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        a = AuthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"username": "me"})):
            assert a.me()["username"] == "me"


class TestHealthClient:
    def test_check(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        h = HealthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"health_score": 85})):
            assert h.check(weight_kg=70)["health_score"] == 85

    def test_list(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        h = HealthClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"total": 1})):
            assert h.list_records()["total"] == 1


class TestEmotionClient:
    def test_analyze(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        e = EmotionClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"summary": "Calm"})):
            assert e.analyze()["summary"] == "Calm"


class TestReportClient:
    def test_generate(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        r = ReportClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"id": 1})):
            assert r.generate()["id"] == 1


class TestTrendClient:
    def test_summary(self):
        c = ApiClient(); c.set_tokens("at", "rt")
        t = TrendClient(c)
        with patch.object(c._session, "request", return_value=_mock_response(200, {"overall_direction": "improving"})):
            assert t.summary()["overall_direction"] == "improving"
