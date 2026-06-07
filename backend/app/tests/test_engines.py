"""Tests for all 8 health check engines."""

import pytest
from app.engines.bmi import calc_bmi
from app.engines.water_ratio import calc_water_ratio
from app.engines.sleep import calc_sleep
from app.engines.activity import calc_activity
from app.engines.diet import calc_diet
from app.engines.mental_healthy import calc_mental_healthy
from app.engines.screen_time import calc_screen_time
from app.engines.habit import calc_habit


class TestBMI:
    def test_healthy_bmi(self):
        result = calc_bmi(65, 175, "English")
        assert result["name"] == "BMI"
        assert result["score"] == 0
        assert result["level"] == "Healthy"
        assert result["metric_value"] == 21.2

    def test_high_bmi(self):
        result = calc_bmi(100, 170, "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"

    def test_low_bmi(self):
        result = calc_bmi(45, 170, "English")
        assert result["score"] == 2
        assert result["level"] == "Medium Risk"

    def test_overweight_bmi(self):
        result = calc_bmi(80, 170, "English")
        assert result["score"] == 1
        assert result["level"] == "Low Risk"

    def test_bmi_chinese(self):
        result = calc_bmi(65, 175, "中文")
        assert result["level"] == "健康"


class TestWaterRatio:
    def test_hydrated(self):
        result = calc_water_ratio(3.0, "A", 70, "A", "A", "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_dehydrated(self):
        result = calc_water_ratio(0.5, "A", 70, "C", "C", "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"


class TestSleep:
    def test_good_sleep(self):
        result = calc_sleep(7.5, 0, "A", "A", "English")
        assert result["name"] == "Sleep"
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_poor_sleep(self):
        result = calc_sleep(4.0, 5, "C", "C", "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"

    def test_moderate_sleep(self):
        result = calc_sleep(5.5, 3, "B", "B", "English")
        assert result["score"] in (1, 2)


class TestActivity:
    def test_active(self):
        result = calc_activity(45, 4, "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_sedentary(self):
        result = calc_activity(5, 12, "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"


class TestDiet:
    def test_good_diet(self):
        result = calc_diet(5, 0, 0, "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_poor_diet(self):
        result = calc_diet(1, 5, 5, "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"


class TestMentalHealth:
    def test_good_mental(self):
        result = calc_mental_healthy("A", "A", "A", "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_poor_mental(self):
        result = calc_mental_healthy("C", "C", "C", "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"


class TestScreenTime:
    def test_balanced_screen(self):
        result = calc_screen_time(3.0, "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_excessive_screen(self):
        result = calc_screen_time(10.0, "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"


class TestHabit:
    def test_good_habits(self):
        result = calc_habit("A", "A", "A", "English")
        assert result["score"] == 0
        assert result["level"] == "Healthy"

    def test_poor_habits(self):
        result = calc_habit("C", "C", "C", "English")
        assert result["score"] == 3
        assert result["level"] == "High Risk"

