"""Shared Matplotlib chart helpers."""

from __future__ import annotations

from functools import lru_cache

import matplotlib
from matplotlib import font_manager


CHINESE_FONT_CANDIDATES = [
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "SimHei",
    "Arial Unicode MS",
]


@lru_cache(maxsize=1)
def resolve_chinese_font() -> str:
    """Return the first available cross-platform CJK font."""
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for font_name in CHINESE_FONT_CANDIDATES:
        if font_name in installed:
            return font_name
    return "DejaVu Sans"


def configure_matplotlib_fonts() -> str:
    """Configure Matplotlib so Chinese labels and minus signs render correctly."""
    font_name = resolve_chinese_font()
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.sans-serif"] = [
        font_name,
        *[name for name in CHINESE_FONT_CANDIDATES if name != font_name],
        "DejaVu Sans",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False
    return font_name

