"""Minimal tests verifying User and RefreshToken models exist and work."""

import pytest
from app.models.user import User
from app.models.refresh_token import RefreshToken


class TestUserModel:
    def test_create_user(self, db_session):
        """Verify we can create and query a user."""
        user = User(
            username="testuser",
            display_name="Test User",
            password_hash="$2b$12$fakehashfortesting",
            preferred_language="English",
        )
        db_session.add(user)
        db_session.flush()

        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_repr(self, db_session):
        user = User(username="reprtest", password_hash="hash")
        db_session.add(user)
        db_session.flush()
        assert "reprtest" in repr(user)

    def test_username_unique(self, db_session):
        """Duplicate usernames should be rejected."""
        db_session.add(User(username="unique", password_hash="hash"))
        db_session.flush()

        dup = User(username="unique", password_hash="hash2")
        db_session.add(dup)
        with pytest.raises(Exception):
            db_session.flush()

    def test_default_language(self, db_session):
        user = User(username="langtest", password_hash="hash")
        db_session.add(user)
        db_session.flush()
        assert user.preferred_language == "English"


class TestRefreshTokenModel:
    def test_create_token(self, db_session):
        """Verify we can create a refresh token linked to a user."""
        from datetime import datetime, timedelta
        import uuid

        user = User(username="tokenuser", password_hash="hash")
        db_session.add(user)
        db_session.flush()

        token = RefreshToken(
            user_id=user.id,
            token_jti=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=7),
            revoked=False,
            created_at=datetime.utcnow(),
        )
        db_session.add(token)
        db_session.flush()

        assert token.id == 1
        assert token.revoked is False
        assert token.user_id == user.id

    def test_token_repr(self, db_session):
        from datetime import datetime, timedelta
        import uuid

        user = User(username="reprtok", password_hash="hash")
        db_session.add(user)
        db_session.flush()

        token = RefreshToken(
            user_id=user.id,
            token_jti=str(uuid.uuid4()),
            expires_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        db_session.add(token)
        db_session.flush()
        assert "reprtok" not in repr(token)  # should reference user_id, not username
        assert str(token.user_id) in repr(token)
