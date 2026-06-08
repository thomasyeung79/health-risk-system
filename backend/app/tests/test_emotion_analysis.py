"""Tests for the emotion analysis service."""

from app.services.emotion_analysis import analyze_emotion
from app.models.emotion_record import EmotionRecord


class TestAnalyzeEmotion:
    def test_full_analysis(self, db_session):
        """Verify analyze_emotion returns all expected fields."""
        result = analyze_emotion(db_session, 1, "English",
            mood_key="Calm", event_key="Nothing special",
            energy=7, stress=3,
        )
        assert result["id"] == 1
        assert result["language"] == "English"
        assert "summary" in result
        assert result["pattern"]["severity"] == "Low"
        assert result["matched_topic"] is not None
        assert result["tonight"] is not None
        assert result["tomorrow"] is not None
        assert "support" in result["guidance"]
        assert result["breathing"]["type"] in ("calming", "pause", "recovery", "basic")
        assert len(result["full_story"]) > 50

    def test_db_persisted(self, db_session):
        """Verify the record was saved to the database."""
        result = analyze_emotion(db_session, 1, "English",
            mood_key="Anxious", event_key="Academic or work-related issue",
            energy=4, stress=8,
        )
        record = db_session.get(EmotionRecord, result["id"])
        assert record is not None
        assert record.mood_key == "Anxious"
        assert record.energy == 4
        assert record.stress == 8
        assert record.pattern_key is not None

    def test_chinese_language(self, db_session):
        """Verify Chinese language output."""
        result = analyze_emotion(db_session, 1, "中文",
            mood_key="Calm", event_key="Nothing special",
            energy=7, stress=3,
        )
        assert result["pattern"]["severity"] == "低"

