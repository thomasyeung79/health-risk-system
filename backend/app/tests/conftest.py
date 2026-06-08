"""pytest fixtures: in-memory SQLite database for testing."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.user import User
from app.services.auth import hash_password, create_access_token


@pytest.fixture(scope="session")
def engine():
    """Create a test engine using an in-memory SQLite database."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a fresh database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user and return (user, password)."""
    password = "testpass123"
    user = User(
        username="testuser",
        display_name="Test User",
        password_hash=hash_password(password),
        preferred_language="English",
    )
    db_session.add(user)
    db_session.flush()
    return user, password


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Return Authorization headers with a valid access token."""
    user, _ = test_user
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
