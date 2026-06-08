"""Unit tests for authentication service."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from jose import jwt

from app.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)


class TestPassword:
    def test_hash_and_verify(self):
        pwd = "securePass123"
        hashed = hash_password(pwd)
        assert hashed != pwd
        assert verify_password(pwd, hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes(self):
        """Same password produces different hashes each time (salt)."""
        h1 = hash_password("test")
        h2 = hash_password("test")
        assert h1 != h2


class TestAccessToken:
    def test_create_and_decode(self):
        token = create_access_token(42)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_decoded_has_expiry(self):
        token = create_access_token(1)
        payload = decode_token(token)
        assert "exp" in payload
        assert "iat" in payload

    def test_tampered_token_fails(self):
        token = create_access_token(1) + "tampered"
        assert decode_token(token) is None


class TestRefreshToken:
    def test_create_and_decode(self):
        token, jti = create_refresh_token(42)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"
        assert payload["jti"] == jti

    def test_unique_jti(self):
        _, jti1 = create_refresh_token(1)
        _, jti2 = create_refresh_token(1)
        assert jti1 != jti2


class TestDecodeToken:
    def test_invalid_token(self):
        assert decode_token("not-a-jwt") is None

    def test_empty_string(self):
        assert decode_token("") is None

    def test_expired_token(self):
        with patch.object(settings, "access_token_expire_minutes", -1):
            token = create_access_token(1)
        assert decode_token(token) is None

    def test_wrong_secret(self):
        token = jwt.encode({"sub": "1"}, "wrong-secret", algorithm="HS256")
        assert decode_token(token) is None


class TestCreateTokenPair:
    def test_persists_refresh_token(self, db_session):
        user = User(username="pairtest", password_hash=hash_password("test"))
        db_session.add(user)
        db_session.flush()

        result = create_token_pair(user, db_session)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["expires_in"] > 0

        # Check DB
        stored = db_session.query(RefreshToken).first()
        assert stored is not None
        assert stored.user_id == user.id
        assert stored.revoked is False


