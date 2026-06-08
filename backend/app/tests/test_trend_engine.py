"""Tests for the trend analysis engine."""

from datetime import datetime, timedelta

import pytest
from app.models.health_record import HealthRecord
from app.models.emotion_record import EmotionRecord
from app.services.trend_engine.config import METRICS
from app.services.trend_engine.metric_analyzer import compute_metric_trend
from app.services.trend_engine.trend_service import compute_summary


def _add_health(db, health_score, sleep_score, days_ago=0, user_id=1):
    dt = datetime.utcnow() - timedelta(days=days_ago)
    r = HealthRecord(
        user_id=user_id, created_at=dt, language="English",
        health_score=health_score, sleep_score=sleep_score,
    )
    db.add(r)
    db.flush()
    return r


def _add_emotion(db, stress, energy, days_ago=0, user_id=1):
    dt = datetime.utcnow() - timedelta(days=days_ago)
    r = EmotionRecord(
        user_id=user_id, created_at=dt, language="English",
        stress=stress, energy=energy,
    )
    db.add(r)
    db.flush()
    return r


class TestMetricAnalyzer:
    def test_health_score_improving(self, db_session):
        _add_health(db_session, 75, 1, days_ago=6)
        _add_health(db_session, 82, 1, days_ago=0)
        result = compute_metric_trend(db_session, 1, "health_score", days=7)
        assert result["direction"] == "improving"
        assert result["change"] == 7.0
        assert result["higher_is_better"] is True

    def test_health_score_declining(self, db_session):
        _add_health(db_session, 85, 1, days_ago=6)
        _add_health(db_session, 75, 2, days_ago=0)
        result = compute_metric_trend(db_session, 1, "health_score", days=7)
        assert result["direction"] == "declining"
        assert result["change"] == -10.0

    def test_health_score_stable(self, db_session):
        _add_health(db_session, 80, 1, days_ago=6)
        _add_health(db_session, 82, 1, days_ago=0)
        result = compute_metric_trend(db_session, 1, "health_score", days=7)
        assert result["direction"] == "stable"
        assert abs(result["change"]) < 5

    def test_stress_improving(self, db_session):
        _add_emotion(db_session, 7, 5, days_ago=6)
        _add_emotion(db_session, 5, 5, days_ago=0)
        result = compute_metric_trend(db_session, 1, "stress", days=7)
        assert result["direction"] == "improving"
        assert result["higher_is_better"] is False

    def test_stress_declining(self, db_session):
        _add_emotion(db_session, 4, 5, days_ago=6)
        _add_emotion(db_session, 7, 5, days_ago=0)
        result = compute_metric_trend(db_session, 1, "stress", days=7)
        assert result["direction"] == "declining"

    def test_energy_improving(self, db_session):
        _add_emotion(db_session, 5, 4, days_ago=6)
        _add_emotion(db_session, 5, 7, days_ago=0)
        result = compute_metric_trend(db_session, 1, "energy", days=7)
        assert result["direction"] == "improving"

    def test_sleep_score_declining(self, db_session):
        _add_health(db_session, 80, 0, days_ago=6)
        _add_health(db_session, 80, 2, days_ago=0)
        result = compute_metric_trend(db_session, 1, "sleep_score", days=7)
        assert result["direction"] == "declining"
        assert result["higher_is_better"] is False

    def test_sleep_score_improving(self, db_session):
        _add_health(db_session, 80, 2, days_ago=6)
        _add_health(db_session, 80, 0, days_ago=0)
        result = compute_metric_trend(db_session, 1, "sleep_score", days=7)
        assert result["direction"] == "improving"

    def test_single_record_insufficient(self, db_session):
        _add_health(db_session, 80, 1, days_ago=0)
        result = compute_metric_trend(db_session, 1, "health_score", days=7)
        assert result["direction"] == "insufficient_data"

    def test_no_records_insufficient(self, db_session):
        result = compute_metric_trend(db_session, 1, "health_score", days=7)
        assert result["direction"] == "insufficient_data"
        assert result["current"] is None

    def test_unknown_metric(self, db_session):
        result = compute_metric_trend(db_session, 1, "nonexistent", days=7)
        assert result["direction"] == "unknown"


class TestTrendSummary:
    def test_empty_db(self, db_session):
        result = compute_summary(db_session, 1, days=7)
        assert result["health_data_points"] == 0
        assert result["emotion_data_points"] == 0
        assert result["overall_direction"] == "insufficient_data"
        assert len(result["metrics"]) == 4

    def test_with_health_data(self, db_session):
        _add_health(db_session, 75, 2, days_ago=6)
        _add_health(db_session, 82, 1, days_ago=0)
        result = compute_summary(db_session, 1, days=7)
        assert result["health_data_points"] == 2
        assert result["emotion_data_points"] == 0
        assert result["metrics"][0]["metric"] == "health_score"

    def test_with_both_data(self, db_session):
        _add_health(db_session, 80, 1, days_ago=5)
        _add_emotion(db_session, 6, 5, days_ago=3)
        _add_emotion(db_session, 4, 6, days_ago=0)
        result = compute_summary(db_session, 1, days=7)
        assert result["health_data_points"] == 1
        assert result["emotion_data_points"] == 2
        assert result["overall_direction"] in ("improving", "stable", "declining", "insufficient_data")

    def test_metrics_structure(self, db_session):
        _add_health(db_session, 80, 1, days_ago=5)
        _add_health(db_session, 82, 0, days_ago=0)
        _add_emotion(db_session, 6, 4, days_ago=5)
        _add_emotion(db_session, 5, 6, days_ago=0)
        result = compute_summary(db_session, 1, days=7)
        for m in result["metrics"]:
            assert "metric" in m
            assert "direction" in m
            assert "higher_is_better" in m
            assert m["direction"] in ("improving", "stable", "declining", "insufficient_data", "unknown")


