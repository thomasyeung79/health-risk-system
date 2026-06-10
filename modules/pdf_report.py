"""PDF Report Generator — exports wellness reports as professional PDF documents.

Supports English and Chinese output using ReportLab.
Chinese text requires a CJK font (Noto Sans CJK or Microsoft YaHei).
"""
import os
from datetime import datetime
from io import BytesIO
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

CJK_FONT_NAME = "Helvetica"


def _find_cjk_font() -> Optional[str]:
    """Find an available CJK font for Chinese PDF output."""
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        os.path.expanduser("~/.fonts/NotoSansCJK-Regular.ttc"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    for win_path in [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]:
        if os.path.exists(win_path):
            return win_path
    return None


def _register_cjk_font():
    """Register a CJK font if available."""
    global CJK_FONT_NAME
    font_path = _find_cjk_font()
    if font_path:
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont("CJK", font_path))
            CJK_FONT_NAME = "CJK"
            return True
        except Exception:
            pass
    return False


_has_cjk = _register_cjk_font()


def _style(font_size=11, bold=False, color="#172026"):
    fn = CJK_FONT_NAME if _has_cjk else "Helvetica"
    if bold:
        fn = fn if _has_cjk else "Helvetica-Bold"
    return ParagraphStyle(
        "s", fontName=fn, fontSize=font_size, leading=font_size * 1.5,
        textColor=colors.HexColor(color), spaceAfter=6,
    )


def _heading_style():
    return ParagraphStyle(
        "h", fontName=CJK_FONT_NAME if _has_cjk else "Helvetica-Bold",
        fontSize=16, leading=24, textColor=colors.HexColor("#0f766e"),
        spaceAfter=12, spaceBefore=8,
    )


def _section_style():
    return ParagraphStyle(
        "sec", fontName=CJK_FONT_NAME if _has_cjk else "Helvetica-Bold",
        fontSize=13, leading=18, textColor=colors.HexColor("#172026"),
        spaceAfter=6, spaceBefore=14,
    )


def generate_pdf(
    user_name: str,
    language: str,
    report_text: str,
    latest_health: Optional[dict] = None,
    latest_mind: Optional[dict] = None,
    history_summary: Optional[dict] = None,
) -> BytesIO:
    """Generate a professional PDF wellness report."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=20*mm, rightMargin=20*mm,
    )

    is_cn = language == "中文"
    elements = []

    # Title
    elements.append(Paragraph(
        "AI Wellness Report" if not is_cn else "AI 健康报告", _heading_style(),
    ))

    # Metadata
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta = f"<b>{'User' if not is_cn else '用户'}:</b> {user_name}<br/>"
    meta += f"<b>{'Date' if not is_cn else '日期'}:</b> {today}<br/>"
    meta += f"<b>{'Language' if not is_cn else '语言'}:</b> {language}"
    elements.append(Paragraph(meta, _style(10, color="#667085")))
    elements.append(Spacer(1, 12))

    # Health Score Summary
    if latest_health:
        elements.append(Paragraph(
            "Health Summary" if not is_cn else "健康摘要", _section_style(),
        ))
        score = latest_health.get("health_score") or latest_health.get("overall_score", "—")
        rl = latest_health.get("risk_level", "—")
        rp = latest_health.get("risk_percent", "—")

        t = Table([
            ["Health Score" if not is_cn else "健康评分",
             "Risk Level" if not is_cn else "风险等级",
             "Risk %" if not is_cn else "风险比例"],
            [str(score), str(rl), f"{rp}%"],
        ], colWidths=[120, 160, 120])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9e2e7")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    # Emotion Summary
    if latest_mind:
        elements.append(Paragraph(
            "Emotional State" if not is_cn else "情绪状态", _section_style(),
        ))
        mood = latest_mind.get("mood") or latest_mind.get("mood_key", "—")
        stress = latest_mind.get("stress", "—")
        energy = latest_mind.get("energy", "—")
        pattern = latest_mind.get("pattern_key", "—")

        t2 = Table([
            ["Mood" if not is_cn else "情绪", "Stress" if not is_cn else "压力",
             "Energy" if not is_cn else "能量", "Pattern" if not is_cn else "模式"],
            [str(mood), f"{stress}/10", f"{energy}/10", str(pattern)],
        ], colWidths=[80, 80, 80, 120])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9e2e7")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 12))

    # Trend Summary
    if history_summary:
        elements.append(Paragraph(
            "Trend Summary" if not is_cn else "趋势摘要", _section_style(),
        ))
        trend = (
            f"<b>{'Health Records' if not is_cn else '健康记录'}:</b> {history_summary.get('health_record_count', 0)} | "
            f"<b>{'Mind Records' if not is_cn else '情绪记录'}:</b> {history_summary.get('mind_record_count', 0)}<br/>"
            f"<b>{'Health Trend' if not is_cn else '健康趋势'}:</b> {history_summary.get('health_score_trend', '—')} | "
            f"<b>{'Stress Trend' if not is_cn else '压力趋势'}:</b> {history_summary.get('stress_trend', '—')}"
        )
        elements.append(Paragraph(trend, _style(10)))
        elements.append(Spacer(1, 12))

    # AI Report Content
    if report_text:
        elements.append(Paragraph(
            "Wellness Analysis" if not is_cn else "健康分析", _section_style(),
        ))
        clean = report_text.replace("## ", "").replace("\n", "<br/>")
        elements.append(Paragraph(clean, _style(10)))
        elements.append(Spacer(1, 12))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"— {user_name} | {today} | WellNest AI —",
        _style(9, color="#94a3b8"),
    ))

    doc.build(elements)
    buf.seek(0)
    return buf
