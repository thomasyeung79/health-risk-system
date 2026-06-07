"""Tests for the health check orchestration service."""

import pytest
from app.services.health_check import run_health_check
from app.models.health_record import HealthRecord


SAMPLE_INPUTS = {
    "weight_kg": 70.0,
    "height_cm": 175.0,
    "water_l": 2.0,
    "situation": "A",
    "thirst_level": "A",
    "urine_color": "A",
    "sleep_hours": 7.5,
    "night_wake_times": 0,
    "difficulty_falling_asleep": "A",
    "irregular_sleep_schedule": "A",
    "exercise_minutes": 30,
    "sedentary_hours": 4,
    "fruit_veg_servings": 5,
    "fast_food_times": 0,
    "sugary_drinks": 0,
    "screen_time_hours": 3.0,
    "smoking": "A",
    "alcohol": "A",
    "late_night": "A",
    "risk_score_emotion": "A",
    "risk_score_focus": "A",
    "risk_score_body": "A",
}


class TestHealthCheck:
    def test_full_health_check(self, db_session):
        """Verify run_health_check returns all expected fields."""
        result = run_health_check(db_session, "English", **SAMPLE_INPUTS)

        # Check response structure
        assert result["id"] == 1
        assert result["language"] == "English"
        assert result["health_score"] == 100.0
        assert result["risk_percent"] == 0.0
        assert result["risk_level"] == "Healthy"

        # Check all 8 modules present
        assert set(result["modules"].keys()) == {
            "BMI", "Water", "Sleep", "Activity",
            "Diet", "Mental", "Screen", "Habit",
        }
        for module_name, module_data in result["modules"].items():
            assert "score" in module_data
            assert "level" in module_data
            assert "reasons" in module_data
            assert "suggestions" in module_data

        assert result["overall"] is not None
        assert result["primary_focus"] is not None
        assert len(result["action_plan"]) > 0

    def test_db_persisted(self, db_session):
        """Verify the record was saved to the database."""
        result = run_health_check(db_session, "English", **SAMPLE_INPUTS)

        record = db_session.get(HealthRecord, result["id"])
        assert record is not None
        assert record.health_score == 100.0
        assert record.weight_kg == 70.0
        assert record.height_cm == 175.0

    def test_high_risk_inputs(self, db_session):
        """Verify high-risk inputs produce appropriate risk levels."""
        high_risk = {
            **SAMPLE_INPUTS,
            "sleep_hours": 3.0,
            "night_wake_times": 6,
            "difficulty_falling_asleep": "C",
            "irregular_sleep_schedule": "C",
            "exercise_minutes": 0,
            "sedentary_hours": 14,
            "smoking": "C",
            "alcohol": "C",
            "late_night": "C",
            "risk_score_emotion": "C",
            "risk_score_focus": "C",
            "risk_score_body": "C",
        }
        result = run_health_check(db_session, "English", **high_risk)
        assert result["risk_level"] in ("Medium Risk", "High Risk")
        assert result["health_score"] < 80

    def test_chinese_language(self, db_session):
        """Verify Chinese language output."""
        result = run_health_check(db_session, "中文", **SAMPLE_INPUTS)
        assert result["risk_level"] == "健康"
        assert result["health_score"] == 100.0

