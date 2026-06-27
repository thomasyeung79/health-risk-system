"""AI Wellness OS — Professional Admin Dashboard."""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from modules.admin_ui import empty_state, metric_card, render_table, section_header, status_badge
from modules.ui import apply_product_theme, render_topbar

st.set_page_config(page_title="Wellness OS", page_icon="W", layout="wide")
apply_product_theme()

language = st.session_state.get("language", "English")
is_cn = language == "中文"

# ── Sidebar navigation ──────────────────────────
PAGES = [
    "Dashboard",
    "Members",
    "Consultations",
    "AI Reports",
    "Healing Plans",
    "Community Cases",
]
PAGES_CN = ["看板", "成员", "咨询记录", "AI 报告", "康复计划", "社区案例"]

page_names = PAGES_CN if is_cn else PAGES
selected = st.sidebar.radio(
    "AI Wellness OS" if not is_cn else "AI 健康管理系统",
    page_names,
    index=0,
)
# Map back to English page key
page_key = PAGES[page_names.index(selected)] if selected in page_names else "Dashboard"

# ── API client ──────────────────────────────────
BACKEND = False
admin_api = None
try:
    from api_client.admin_client import AdminClient

    if "api_client" in st.session_state:
        _c = st.session_state["api_client"]
    else:
        from api_client.client import ApiClient
        _c = ApiClient()
        st.session_state["api_client"] = _c

    if st.session_state.get("access_token"):
        _c.set_tokens(st.session_state["access_token"], st.session_state.get("refresh_token", ""))
    h = _c.get("/health")
    if h.get("status") == "ok" and _c.is_authenticated:
        BACKEND = True
        admin_api = AdminClient(_c)
except Exception:
    pass

st.sidebar.markdown("---")
user_name = st.session_state.get("user_name", "")
st.sidebar.write(f"👤 {user_name}")
if st.sidebar.button("🚪 Logout" if not is_cn else "🚪 退出"):
    for k in ["access_token", "refresh_token", "api_user", "user_name", "authenticated"]:
        st.session_state.pop(k, None)
    st.switch_page("web_v1.py")


def api_error_message(exc: Exception) -> str:
    """Return a user-safe API error message."""
    detail = getattr(exc, "detail", "") or str(exc)
    return detail[:180] if detail else ("Request failed." if not is_cn else "请求失败。")


def friendly_api_error(exc: Exception):
    st.error(("Request failed: " if not is_cn else "请求失败：") + api_error_message(exc))


def format_created_at(df: pd.DataFrame) -> pd.DataFrame:
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def existing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [c for c in columns if c in df.columns]


# ═══════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════
def render_dashboard():
    section_header(
        "Dashboard" if not is_cn else "管理看板",
        "AI Wellness OS Overview" if not is_cn else "AI 健康管理系统概览",
    )

    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接",
                     "Start the backend server to use the admin dashboard." if not is_cn else "请启动后端服务器。")
        return

    try:
        data = admin_api.dashboard_summary()
    except Exception as e:
        empty_state("⚠️", "Error Loading Data" if not is_cn else "加载数据失败",
                     api_error_message(e))
        return

    kpi_cols = st.columns(5)
    kpis = [
        ("👥", "Total Members" if not is_cn else "成员总数", data.get("total_members", 0)),
        ("📋", "Consultations" if not is_cn else "咨询记录", data.get("total_consultations", 0)),
        ("📊", "AI Reports" if not is_cn else "AI 报告", data.get("total_ai_reports", 0)),
        ("🎯", "Healing Plans" if not is_cn else "康复计划", data.get("total_healing_plans", 0)),
        ("📂", "Community Cases" if not is_cn else "社区案例", data.get("total_community_cases", 0)),
    ]
    for col, (icon, label, value) in zip(kpi_cols, kpis):
        with col:
            metric_card(label, value, prefix="")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)

    with r1:
        st.markdown("#### 👥 Recent Members" if not is_cn else "#### 👥 最近成员")
        members = data.get("recent_members", [])
        if members:
            df = pd.DataFrame(members)
            df = format_created_at(df)
            cols = existing_columns(df, ["name", "age", "gender", "country", "created_at"])
            render_table(df[cols] if cols else df)
        else:
            st.info("No members yet." if not is_cn else "暂无成员。")

    with r2:
        st.markdown("#### 📋 Recent Consultations" if not is_cn else "#### 📋 最近咨询")
        consults = data.get("recent_consultations", [])
        if consults:
            df = pd.DataFrame(consults)
            df = format_created_at(df)
            cols = existing_columns(df, ["member_id", "consultation_type", "created_at"])
            render_table(df[cols] if cols else df)
        else:
            st.info("No consultations yet." if not is_cn else "暂无咨询记录。")


# ═══════════════════════════════════════════════════
# MEMBERS
# ═══════════════════════════════════════════════════
def render_members():
    section_header(
        "Member Management" if not is_cn else "成员管理",
        "Create, edit, and manage wellness members." if not is_cn else "创建、编辑和管理健康成员。",
    )

    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    tab_list, tab_create = st.tabs(
        ["📋 Member List" if not is_cn else "📋 成员列表",
         "➕ New Member" if not is_cn else "➕ 新增成员"] if not is_cn else
        ["📋 成员列表", "➕ 新增成员"]
    )

    with tab_list:
        try:
            resp = admin_api.list_members(limit=100)
            items = resp.get("items", [])
            if items:
                df = pd.DataFrame(items)
                df = format_created_at(df)
                cols = ["id", "name", "age", "gender", "country", "preferred_language", "created_at"]
                cols = existing_columns(df, cols)
                render_table(df[cols])
                st.caption(f"Total: {resp.get('total', len(items))} members" if not is_cn else f"共 {resp.get('total', len(items))} 名成员")
            else:
                empty_state("👥", "No Members Yet" if not is_cn else "暂无成员",
                            "Create your first member to get started." if not is_cn else "创建第一个成员开始使用。")
        except Exception as e:
            friendly_api_error(e)

    with tab_create:
        with st.form("create_member"):
            name = st.text_input("Name *" if not is_cn else "姓名 *")
            col1, col2 = st.columns(2)
            with col1:
                gender = st.selectbox("Gender" if not is_cn else "性别", [""] + (["Female", "Male", "Other"] if not is_cn else ["女", "男", "其他"]))
                age = st.number_input("Age" if not is_cn else "年龄", 0, 150, 30)
            with col2:
                country = st.text_input("Country" if not is_cn else "国家")
                lang = st.selectbox("Language" if not is_cn else "语言", ["English", "中文"])
            notes = st.text_area("Notes" if not is_cn else "备注")
            if st.form_submit_button("Create Member" if not is_cn else "创建成员", use_container_width=True):
                if name.strip():
                    try:
                        payload = {"name": name.strip(), "age": age, "preferred_language": lang}
                        if gender:
                            payload["gender"] = gender
                        if country:
                            payload["country"] = country
                        if notes:
                            payload["notes"] = notes
                        admin_api.create_member(**payload)
                        st.success("Member created!" if not is_cn else "成员创建成功！")
                        st.rerun()
                    except Exception as e:
                        friendly_api_error(e)
                else:
                    st.error("Name is required." if not is_cn else "请填写姓名。")


# ═══════════════════════════════════════════════════
# CONSULTATIONS
# ═══════════════════════════════════════════════════
def render_consultations():
    section_header(
        "Consultation Center" if not is_cn else "咨询中心",
        "Track and manage wellness consultations." if not is_cn else "跟踪和管理健康咨询。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    try:
        resp = admin_api.list_consultations(limit=100)
        items = resp.get("items", [])
        if items:
            df = pd.DataFrame(items)
            df = format_created_at(df)
            cols = existing_columns(df, ["id", "member_id", "consultation_type", "main_concern", "created_at"])
            render_table(df[cols] if cols else df)
        else:
            empty_state("📋", "No Consultations" if not is_cn else "暂无咨询记录",
                        "Create a member first, then add consultations." if not is_cn else "请先创建成员。")
    except Exception as e:
        friendly_api_error(e)

    st.markdown("---")
    st.markdown("#### New Consultation" if not is_cn else "#### 新建咨询")
    with st.form("create_consultation"):
        mid = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1)
        ctype = st.text_input("Consultation Type" if not is_cn else "咨询类型", placeholder="initial / follow-up / emergency")
        concern = st.text_area("Main Concern" if not is_cn else "主要问题")
        if st.form_submit_button("Create Consultation" if not is_cn else "创建咨询", use_container_width=True):
            if not ctype.strip() and not concern.strip():
                st.error("Add a consultation type or main concern." if not is_cn else "请填写咨询类型或主要问题。")
                st.stop()
            try:
                admin_api.create_consultation(
                    member_id=int(mid),
                    consultation_type=ctype.strip() or None,
                    main_concern=concern.strip() or None,
                )
                st.success("Consultation created!" if not is_cn else "咨询创建成功！")
                st.rerun()
            except Exception as e:
                friendly_api_error(e)


# ═══════════════════════════════════════════════════
# AI REPORTS
# ═══════════════════════════════════════════════════
def render_ai_reports():
    section_header(
        "AI Report Center" if not is_cn else "AI 报告中心",
        "Generate and review AI-powered wellness reports." if not is_cn else "生成和查看 AI 健康报告。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    col_gen, col_list = st.columns([1, 2])

    with col_gen:
        st.markdown("#### Generate Report" if not is_cn else "#### 生成报告")
        mid = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="report_mid")
        if st.button("Generate AI Report" if not is_cn else "生成 AI 报告", use_container_width=True, type="primary"):
            try:
                report = admin_api.generate_ai_report(member_id=int(mid))
                st.success("Report generated!" if not is_cn else "报告生成成功！")
                summary = report.get("summary") or ""
                st.json({
                    "summary": summary[:100] + ("..." if len(summary) > 100 else ""),
                    "risk_level": report.get("risk_level") or "",
                    "model": report.get("model_used") or "",
                })
            except Exception as e:
                friendly_api_error(e)

    with col_list:
        st.markdown("#### Recent Reports" if not is_cn else "#### 最近报告")
        try:
            resp = admin_api.list_ai_reports(limit=20)
            items = resp.get("items", [])
            if items:
                df = pd.DataFrame(items)
                df = format_created_at(df)
                if "risk_level" in df.columns:
                    df["risk"] = df["risk_level"].apply(lambda x: status_badge(x or ""))
                cols = existing_columns(df, ["id", "member_id", "risk_level", "model_used", "created_at"])
                render_table(df[cols] if cols else df)
            else:
                st.info("No reports yet." if not is_cn else "暂无报告。")
        except Exception as e:
            friendly_api_error(e)


# ═══════════════════════════════════════════════════
# HEALING PLANS
# ═══════════════════════════════════════════════════
def render_healing_plans():
    section_header(
        "Healing Plans" if not is_cn else "康复计划",
        "Manage wellness plans for members." if not is_cn else "管理成员康复计划。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    try:
        resp = admin_api.list_healing_plans(limit=100)
        items = resp.get("items", [])
        if items:
            df = pd.DataFrame(items)
            df = format_created_at(df)
            if "status" in df.columns:
                df["status_badge"] = df["status"].apply(lambda x: status_badge(x or ""))
            cols = existing_columns(df, ["id", "member_id", "title", "status", "created_at"])
            render_table(df[cols] if cols else df)
        else:
            empty_state("🎯", "No Healing Plans" if not is_cn else "暂无康复计划",
                        "Create a healing plan for a member." if not is_cn else "为成员创建康复计划。")
    except Exception as e:
        friendly_api_error(e)

    st.markdown("---")
    st.markdown("#### New Plan" if not is_cn else "#### 新建计划")
    with st.form("create_plan"):
        mid = st.number_input("Member ID", min_value=1, step=1, key="plan_mid")
        title = st.text_input("Plan Title *" if not is_cn else "计划标题 *")
        desc = st.text_area("Description" if not is_cn else "描述")
        if st.form_submit_button("Create Plan" if not is_cn else "创建计划", use_container_width=True):
            if title.strip():
                try:
                    admin_api.create_healing_plan(member_id=int(mid), title=title.strip(), description=desc)
                    st.success("Plan created!" if not is_cn else "计划创建成功！")
                    st.rerun()
                except Exception as e:
                    friendly_api_error(e)
            else:
                st.error("Plan title is required." if not is_cn else "请填写计划标题。")


# ═══════════════════════════════════════════════════
# COMMUNITY CASES
# ═══════════════════════════════════════════════════
def render_community_cases():
    section_header(
        "Community Cases" if not is_cn else "社区案例",
        "Anonymised wellness case studies." if not is_cn else "匿名健康案例研究。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    try:
        resp = admin_api.list_community_cases(limit=100, public_only=False)
        items = resp.get("items", [])
        if items:
            for case in items:
                with st.container(border=True):
                    cc, cm = st.columns([3, 1])
                    with cc:
                        st.markdown(f"**{case.get('title', '')}**")
                        if case.get("anonymized_summary"):
                            st.caption(case["anonymized_summary"][:200])
                    with cm:
                        st.markdown(f"`{case.get('category', '')}`  {status_badge('active')}")
                        if case.get("language"):
                            st.caption(f"🌐 {case['language']}")
                        if case.get("is_public"):
                            st.caption("🌍 Public" if not is_cn else "🌍 公开")
        else:
            empty_state("📂", "No Community Cases" if not is_cn else "暂无社区案例",
                        "Share anonymised cases with the community." if not is_cn else "分享匿名案例。")
    except Exception as e:
        friendly_api_error(e)

    st.markdown("---")
    st.markdown("#### Share Case" if not is_cn else "#### 分享案例")
    with st.form("create_case"):
        title = st.text_input("Title *" if not is_cn else "标题 *")
        cat = st.selectbox("Category" if not is_cn else "分类",
                           ["sleep", "stress", "fitness", "nutrition", "mental_health", "general"])
        summary = st.text_area("Anonymized Summary" if not is_cn else "匿名摘要")
        approach = st.text_area("Healing Approach" if not is_cn else "康复方法")
        outcome = st.text_area("Outcome" if not is_cn else "结果")
        public = st.checkbox("Make Public" if not is_cn else "公开发布", True)
        if st.form_submit_button("Submit Case" if not is_cn else "提交案例", use_container_width=True):
            if title.strip():
                try:
                    admin_api.create_community_case(
                        title=title.strip(), category=cat, anonymized_summary=summary,
                        healing_approach=approach, outcome=outcome, is_public=public,
                    )
                    st.success("Case shared!" if not is_cn else "案例分享成功！")
                    st.rerun()
                except Exception as e:
                    friendly_api_error(e)
            else:
                st.error("Case title is required." if not is_cn else "请填写案例标题。")


# ═══════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════
PAGE_RENDERERS = {
    "Dashboard": render_dashboard,
    "Members": render_members,
    "Consultations": render_consultations,
    "AI Reports": render_ai_reports,
    "Healing Plans": render_healing_plans,
    "Community Cases": render_community_cases,
}

render_fn = PAGE_RENDERERS.get(page_key, render_dashboard)
render_fn()
