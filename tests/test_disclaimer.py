"""Tests for the bilingual medical disclaimer."""

from modules.ui import DISCLAIMER


def test_english_disclaimer_exists():
    """English disclaimer must be present and non-empty."""
    text = DISCLAIMER.get("English", "")
    assert text, "English disclaimer is missing or empty"


def test_chinese_disclaimer_exists():
    """Chinese disclaimer must be present and non-empty."""
    text = DISCLAIMER.get("中文", "")
    assert text, "Chinese disclaimer is missing or empty"


def test_english_disclaimer_indicates_informational_use():
    """English disclaimer must state informational/educational purpose."""
    text = DISCLAIMER["English"]
    assert "informational" in text.lower() or "educational" in text.lower(), \
        "Must indicate informational/educational purpose"


def test_english_disclaimer_not_medical_advice():
    """English disclaimer must clearly state it is not medical advice."""
    text = DISCLAIMER["English"]
    assert "not" in text.lower() and ("medical" in text.lower() or "diagnosis" in text.lower()), \
        "Must state it does not provide medical diagnosis"


def test_english_disclaimer_consult_professional():
    """English disclaimer must advise consulting a professional."""
    text = DISCLAIMER["English"]
    assert "consult" in text.lower() or "healthcare professional" in text.lower(), \
        "Must advise consulting a healthcare professional"


def test_chinese_disclaimer_indicates_informational_use():
    """Chinese disclaimer must state informational/educational purpose."""
    text = DISCLAIMER["中文"]
    assert "参考" in text or "教育" in text, "Must indicate informational/educational purpose"


def test_chinese_disclaimer_not_medical_advice():
    """Chinese disclaimer must clearly state it is not medical advice."""
    text = DISCLAIMER["中文"]
    assert "不" in text and ("医疗" in text or "诊断" in text or "治疗" in text), \
        "Must state it does not provide medical diagnosis/treatment"


def test_chinese_disclaimer_consult_professional():
    """Chinese disclaimer must advise consulting a professional."""
    text = DISCLAIMER["中文"]
    assert "咨询" in text and ("专业" in text or "医疗人员" in text), \
        "Must advise consulting a qualified professional"
