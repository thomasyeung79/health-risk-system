"""Tests for dashboard insight generation."""

from modules.dashboard_insights import build_trend_insights


def test_empty_data_returns_empty_list():
    assert build_trend_insights({}, "English") == []
    assert build_trend_insights({
        "health": None,
        "emotion": None,
        "trends": None,
        "health_stats": None,
        "emotion_stats": None,
    }, "English") == []


def test_trend_metrics_produce_english_insights():
    data = {
        "trends": {
            "metrics": [
                {"metric": "health_score", "current": 85, "previous": 80, "change": 5, "direction": "improving"},
                {"metric": "stress", "current": 6, "previous": 7, "change": -1, "direction": "declining"},
            ]
        }
    }

    insights = build_trend_insights(data, "English")

    assert insights[0]["text"] == "Health score increased by 5 pts this week (current: 85)."
    assert insights[1]["text"] == "Stress decreased by 1 pt this week (current: 6)."


def test_trend_metrics_produce_chinese_insights():
    data = {
        "trends": {
            "metrics": [
                {"metric": "health_score", "current": 85, "previous": 80, "change": 5, "direction": "improving"},
                {"metric": "stress", "current": 6, "previous": 7, "change": -1, "direction": "declining"},
            ]
        }
    }

    insights = build_trend_insights(data, "中文")

    assert insights[0]["text"] == "本周健康评分上升 5 分（当前：85）。"
    assert insights[1]["text"] == "本周压力下降 1 分（当前：6）。"


def test_cross_domain_sleep_stress_insight():
    data = {
        "health": {"sleep_score": 2},
        "emotion": {"stress": 7},
    }

    insights = build_trend_insights(data, "English")

    assert any(
        insight["text"] == "Sleep quality and stress may be reinforcing each other."
        for insight in insights
    )


def test_cross_domain_activity_energy_insight():
    data = {
        "health": {"activity_score": 2},
        "emotion": {"energy": 3},
    }

    insights = build_trend_insights(data, "English")

    assert any(
        insight["text"] == "Low activity may be affecting your energy level."
        for insight in insights
    )


def test_priority_recommendation_from_worst_module():
    data = {
        "health": {
            "sleep_score": 1,
            "activity_score": 3,
            "diet_score": 2,
        }
    }

    insights = build_trend_insights(data, "English")

    assert any(
        insight["text"] == "Add at least 20 minutes of movement daily."
        for insight in insights
    )


def test_high_stress_adds_breathing_recommendation():
    data = {
        "emotion": {"stress": 8},
    }

    insights = build_trend_insights(data, "English")

    assert any(
        insight["text"] == "Try a 5-minute breathing exercise today."
        for insight in insights
    )


def test_malformed_data_does_not_raise():
    data = {
        "health": "bad",
        "emotion": {"stress": "not-a-number"},
        "trends": {"metrics": [None, "bad", {"metric": "health_score"}]},
    }

    assert build_trend_insights(data, "English") == []
    assert build_trend_insights(None, "English") == []


def test_output_limited_to_four_insights():
    data = {
        "health": {"sleep_score": 3, "activity_score": 2},
        "emotion": {"stress": 8, "energy": 2},
        "trends": {
            "metrics": [
                {"metric": "health_score", "current": 80, "previous": 70, "change": 10, "direction": "improving"},
                {"metric": "stress", "current": 8, "previous": 6, "change": 2, "direction": "declining"},
                {"metric": "energy", "current": 2, "previous": 5, "change": -3, "direction": "declining"},
            ]
        },
    }

    insights = build_trend_insights(data, "English")

    assert len(insights) == 4
