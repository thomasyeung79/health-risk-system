"""AI Wellness OS — reusable admin UI components for Streamlit."""

import pandas as pd
import streamlit as st


def metric_card(label: str, value, prefix="", suffix="", delta=None):
    """Professional metric card with colored accent bar."""
    delta_html = f'<div style="font-size:13px;color:#22c55e;margin-top:4px;">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div style="
        background:white;border-radius:10px;padding:20px;border:1px solid #e5e7eb;
        border-left:4px solid #0f766e;box-shadow:0 1px 3px rgba(0,0,0,0.04);
    ">
        <div style="font-size:13px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:#172026;margin:4px 0 0 0;">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Return HTML for a status badge."""
    colors = {
        "active": "#dcfce7, #15803d", "completed": "#dbeafe, #2563eb",
        "inactive": "#f1f5f9, #64748b", "Low": "#dcfce7, #15803d",
        "Medium": "#fef9c3, #a16207", "High": "#fee2e2, #b91c1c",
        "healthy": "#dcfce7, #15803d", "Healthy": "#dcfce7, #15803d",
        "低": "#dcfce7, #15803d", "中": "#fef9c3, #a16207", "高": "#fee2e2, #b91c1c",
    }
    bg, fg = colors.get(status, "#f1f5f9, #64748b").split(", ")
    return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;">{status}</span>'


def section_header(title: str, subtitle: str = ""):
    """Page section header."""
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:22px;font-weight:800;color:#172026;">{title}</div>
        {f'<div style="font-size:14px;color:#64748b;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_table(df: pd.DataFrame, max_rows=25):
    """Render a DataFrame as a clean table."""
    if df.empty:
        st.info("No data to display.")
        return
    st.dataframe(df.head(max_rows), use_container_width=True, hide_index=True)


def empty_state(icon: str, title: str, description: str):
    """Professional empty state."""
    st.markdown(f"""
    <div style="text-align:center;padding:60px 20px;background:white;border-radius:12px;border:1px solid #e5e7eb;">
        <div style="font-size:48px;margin-bottom:12px;">{icon}</div>
        <div style="font-size:20px;font-weight:700;color:#172026;margin-bottom:8px;">{title}</div>
        <div style="font-size:14px;color:#64748b;max-width:400px;margin:0 auto;">{description}</div>
    </div>
    """, unsafe_allow_html=True)
