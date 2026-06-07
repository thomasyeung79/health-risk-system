"""Tests for the health analyzer service."""

import pytest
from app.services.health_analyzer import calculate_overall_result, LEVEL_TEXTS, dedup


def make_result(name, score=0, level="Healthy", max_score=3):
    return {
        "name": name,
        "score": score,
        "level": level,
        "max_score": max_score,
        "category": "Test",
        "metric_value": 0,
        "reasons": [],
        "suggestions": [],
    }


class TestDedup:
    def test_dedup_basic(self):
        assert dedup([1, 2, 2, 3]) == [1, 2, 3]

    def test_dedup_empty(self):
        assert dedup([]) == []


class TestLevelTexts:
    def test_english_levels(self):
        assert LEVEL_TEXTS["English"]["healthy"] == "Healthy"
        assert LEVEL_TEXTS["English"]["high"] == "High Risk"

    def test_chinese_levels(self):
        assert LEVEL_TEXTS["中文"]["healthy"] == "健康"
        assert LEVEL_TEXTS["中文"]["high"] == "高风险"


class TestCalculateOverall:
    def test_all_healthy(self):
        results = [make_result(name) for name in ["BMI", "Water", "Sleep", "Activity", "Diet", "Mental", "Screen", "Habit"]]
        overall = calculate_overall_result(results, "English")
        assert overall["health_score"] == 100.0
        assert overall["risk_level"] == "Healthy"
        assert overall["risk_percent"] == 0.0

    def test_all_high_risk(self):
        results = [make_result(name, score=3, level="High Risk") for name in ["BMI", "Water", "Sleep", "Activity", "Diet", "Mental", "Screen", "Habit"]]
        overall = calculate_overall_result(results, "English")
        assert overall["health_score"] <= 40.0
        assert overall["risk_level"] == "High Risk"
        assert overall["risk_percent"] >= 60.0

    def test_mixed_risk(self):
        results = [
            make_result("BMI", score=0),
            make_result("Water", score=1),
            make_result("Sleep", score=2),
            make_result("Activity", score=0),
            make_result("Diet", score=1),
            make_result("Mental", score=0),
            make_result("Screen", score=0),
            make_result("Habit", score=0),
        ]
        overall = calculate_overall_result(results, "English")
        assert 0 < overall["health_score"] < 100
        assert overall["risk_level"] in ("Healthy", "Low Risk")

    def test_priority_focus(self):
        results = [
            make_result("BMI", score=3, level="High Risk"),
            make_result("Water", score=2, level="Medium Risk"),
            make_result("Sleep", score=1, level="Low Risk"),
        ] + [make_result(name) for name in ["Activity", "Diet", "Mental", "Screen", "Habit"]]
        overall = calculate_overall_result(results, "English")
        assert "weight balance" in overall["primary_focus"]
        assert len(overall["action_plan"]) > 0

    def test_chinese_output(self):
        results = [make_result(name, score=0) for name in ["BMI", "Water", "Sleep", "Activity", "Diet", "Mental", "Screen", "Habit"]]
        overall = calculate_overall_result(results, "中文")
        assert overall["risk_level"] == "健康"
        assert overall["primary_focus"] == "目前没有明显高风险模块，重点是保持节奏并继续观察变化。"

