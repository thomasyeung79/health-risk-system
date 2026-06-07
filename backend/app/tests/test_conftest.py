"""Verify the test database fixture works correctly."""

from app.models.health_record import HealthRecord


def test_conftest_fixture(db_session):
    """Verify that the db_session fixture creates a working in-memory database."""
    record = HealthRecord(
        language="en",
        weight_kg=70.0,
        height_cm=175.0,
        health_score=85.0,
        risk_level="Low Risk",
    )
    db_session.add(record)
    db_session.flush()

    assert record.id == 1

    fetched = db_session.get(HealthRecord, 1)
    assert fetched is not None
    assert fetched.weight_kg == 70.0
    assert fetched.health_score == 85.0
    assert fetched.risk_level == "Low Risk"
    assert fetched.created_at is not None


def test_conftest_isolation(db_session):
    """Verify each test gets a clean database."""
    count = db_session.query(HealthRecord).count()
    assert count == 0, "Database should be empty for each test"
