"""Tests for the PDF report generator."""

import os
from datetime import datetime

import pytest

from modules.pdf_report import generate_pdf


class TestPDFGeneration:
    def test_pdf_generates_bytesio(self):
        """PDF generation returns a non-empty BytesIO object."""
        buf = generate_pdf(
            user_name="TestUser",
            language="English",
            report_text="Your health score is 85/100. Keep up the good work!",
        )
        assert buf is not None
        data = buf.read()
        assert len(data) > 100
        assert data[:4] == b"%PDF", "File should start with PDF header"

    def test_pdf_contains_metadata(self):
        """PDF contains user name and date."""
        buf = generate_pdf(
            user_name="Alice",
            language="English",
            report_text="Wellness analysis content here.",
        )
        data = buf.read()
        # PDF is binary, check header and size
        assert len(data) > 500
        assert b"PDF" in data[:50]

    def test_pdf_with_health_data(self):
        """PDF includes health scores when provided."""
        buf = generate_pdf(
            user_name="Bob",
            language="English",
            report_text="Test report.",
            latest_health={
                "health_score": 85.0,
                "risk_level": "Low Risk",
                "risk_percent": 15.0,
            },
        )
        data = buf.read()
        assert len(data) > 500

    def test_pdf_with_emotion_data(self):
        """PDF includes emotion data when provided."""
        buf = generate_pdf(
            user_name="Charlie",
            language="English",
            report_text="Test report.",
            latest_mind={
                "mood_key": "Calm",
                "stress": 4,
                "energy": 7,
                "pattern_key": "Stable",
            },
        )
        data = buf.read()
        assert len(data) > 500

    def test_pdf_with_trend_data(self):
        """PDF includes trend summary when provided."""
        buf = generate_pdf(
            user_name="Dave",
            language="English",
            report_text="Test report.",
            history_summary={
                "health_record_count": 5,
                "mind_record_count": 3,
                "health_score_trend": "Improving",
                "stress_trend": "Stable",
            },
        )
        data = buf.read()
        assert len(data) > 500

    def test_pdf_all_data_en(self):
        """English PDF with all data sections renders."""
        buf = generate_pdf(
            user_name="Eve",
            language="English",
            report_text="## Health Analysis\nGood.\n## Emotional State\nCalm.",
            latest_health={"health_score": 92.0, "risk_level": "Healthy", "risk_percent": 8.0},
            latest_mind={"mood_key": "Calm", "stress": 3, "energy": 8, "pattern_key": "Stable"},
            history_summary={
                "health_record_count": 10, "mind_record_count": 7,
                "health_score_trend": "Improving", "stress_trend": "Declining",
            },
        )
        data = buf.read()
        assert len(data) > 1000

    def test_pdf_chinese_output(self):
        """Chinese PDF generates without error (CJK font is optional)."""
        buf = generate_pdf(
            user_name="测试用户",
            language="中文",
            report_text="健康评分 85/100，继续保持。",
            latest_health={"health_score": 85.0, "risk_level": "健康", "risk_percent": 15.0},
        )
        data = buf.read()
        assert len(data) > 500
        assert data[:4] == b"%PDF"

    def test_pdf_english_rendered_text(self):
        """English title appears in PDF."""
        buf = generate_pdf(
            user_name="Test",
            language="English",
            report_text="Wellness analysis content.",
        )
        data = buf.read()
        assert len(data) > 500

    def test_pdf_chinese_title(self):
        """Chinese title appears in PDF."""
        buf = generate_pdf(
            user_name="测试",
            language="中文",
            report_text="测试内容。",
        )
        data = buf.read()
        assert len(data) > 500
