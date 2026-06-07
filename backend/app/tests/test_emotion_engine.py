"""Tests for the emotion analysis engine."""

import pytest
from app.engines.emotion import (
    detect_emotional_pattern,
    auto_select_topic,
    generate_summary,
    generate_tonight,
    generate_tomorrow,
    generate_reflection_guidance,
    generate_breathing_practice,
    run_reflection_engine,
)


class TestDetectPattern:
    def test_burnout_risk(self):
        result = detect_emotional_pattern([], [], 8, 2, "English")
        assert result["pattern"] == "Burnout Risk"
        assert result["severity"] == "High"

    def test_anxiety(self):
        result = detect_emotional_pattern(["Anxious"], [], 5, 5, "English")
        assert result["pattern"] == "Overthinking / Anxiety State"

    def test_emotional_tension(self):
        result = detect_emotional_pattern(["Angry"], [], 5, 5, "English")
        assert result["pattern"] == "Emotional Tension"

    def test_recovery_need_tired(self):
        result = detect_emotional_pattern(["Tired"], [], 5, 5, "English")
        assert result["pattern"] == "Recovery Need"

    def test_recovery_need_low_energy(self):
        result = detect_emotional_pattern([], [], 5, 2, "English")
        assert result["pattern"] == "Recovery Need"

    def test_suppression(self):
        result = detect_emotional_pattern(["Numb"], [], 5, 5, "English")
        assert result["pattern"] == "Emotional Suppression"

    def test_stable(self):
        result = detect_emotional_pattern(["Calm"], [], 2, 7, "English")
        assert result["pattern"] == "Stable / Balanced State"
        assert result["severity"] == "Low"

    def test_general(self):
        result = detect_emotional_pattern(["Low"], [], 5, 5, "English")
        assert result["pattern"] == "General Reflection State"

    def test_chinese_burnout(self):
        result = detect_emotional_pattern([], [], 8, 2, "中文")
        assert result["pattern"] == "过载风险"
        assert result["severity"] == "高"


class TestAutoSelectTopic:
    def test_high_stress(self):
        assert auto_select_topic([], [], 8, 5) == "Pressure Recovery"

    def test_anxious(self):
        assert auto_select_topic(["Anxious"], [], 5, 5) == "Emotional Awareness"

    def test_angry(self):
        assert auto_select_topic(["Angry"], [], 5, 5) == "Pause Before Reaction"

    def test_tired(self):
        assert auto_select_topic(["Tired"], [], 5, 5) == "Rest and Renewal"

    def test_academic(self):
        r = auto_select_topic([], ["Academic or work-related issue"], 5, 5)
        assert r == "Discipline and Action"

    def test_calm(self):
        assert auto_select_topic(["Calm"], [], 2, 7) == "Gratitude and Balance"


class TestSummary:
    def test_high_stress(self):
        s = generate_summary([], [], 8, 2, "English")
        assert "strong pressure" in s

    def test_chinese_high_stress(self):
        s = generate_summary([], [], 8, 2, "中文")
        assert "降低负荷" in s


class TestBreathing:
    def test_calming(self):
        b = generate_breathing_practice(["Anxious"], 8, 5, "English")
        assert b["type"] == "calming"

    def test_pause(self):
        b = generate_breathing_practice(["Angry"], 5, 5, "English")
        assert b["type"] == "pause"

    def test_recovery(self):
        b = generate_breathing_practice(["Tired"], 5, 2, "English")
        assert b["type"] == "recovery"

    def test_basic(self):
        b = generate_breathing_practice(["Calm"], 3, 7, "English")
        assert b["type"] == "basic"


class TestGuidance:
    def test_structure(self):
        g = generate_reflection_guidance("Emotional Awareness", "English")
        assert "topic" in g
        assert "support" in g
        assert "practice" in g


class TestRunEngine:
    def test_full_structure(self):
        result = run_reflection_engine(["Calm"], ["Nothing special"], 3, 7, "English")
        keys = {"summary", "pattern", "matched_topic", "tonight", "tomorrow", "guidance", "breathing", "story"}
        assert keys.issubset(result.keys())

    def test_chinese_output(self):
        result = run_reflection_engine(["Calm"], ["Nothing special"], 3, 7, "中文")
        assert result["pattern"]["severity"] == "低"
