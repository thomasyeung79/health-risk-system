"""AI Wellness OS — Professional Administration Dashboard."""

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
    "Growth Journey",
    "Insights",
    "Member Workspace",
]
PAGES_CN = ["看板", "成员", "咨询记录", "AI 报告", "康复计划", "社区案例", "成长之旅", "智能洞察", "成员工作区"]

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
                     "Start the backend server to use Administration." if not is_cn else "请启动后端服务器后使用管理中心。")
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
            empty_state("👥", "No Recent Members" if not is_cn else "暂无最近成员",
                        "Create members to populate this overview." if not is_cn else "创建成员后这里会显示最近成员。")

    with r2:
        st.markdown("#### 📋 Recent Consultations" if not is_cn else "#### 📋 最近咨询")
        consults = data.get("recent_consultations", [])
        if consults:
            df = pd.DataFrame(consults)
            df = format_created_at(df)
            cols = existing_columns(df, ["member_id", "consultation_type", "created_at"])
            render_table(df[cols] if cols else df)
        else:
            empty_state("📋", "No Recent Consultations" if not is_cn else "暂无最近咨询",
                        "New consultations will appear here." if not is_cn else "新增咨询后这里会显示最近记录。")


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
                empty_state("📊", "No AI Reports Yet" if not is_cn else "暂无 AI 报告",
                            "Generate a report for a member to review it here." if not is_cn else "为成员生成报告后将在这里显示。")
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
        mid = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="plan_mid")
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
# GROWTH JOURNEY
# ═══════════════════════════════════════════════════
def render_growth_journey():
    section_header(
        "Growth Journey" if not is_cn else "成长之旅",
        "Personal wellness growth timeline for members." if not is_cn else "成员个人健康成长的历程展示。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    col_gen, col_list = st.columns([1, 2])

    with col_gen:
        st.markdown("#### Generate Journey" if not is_cn else "#### 生成成长之旅")
        mid = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="gj_mid")
        if st.button("Generate Growth Journey" if not is_cn else "生成成长之旅", use_container_width=True, type="primary"):
            try:
                journey = admin_api.generate_growth_journey(member_id=int(mid))
                st.success("Journey generated!" if not is_cn else "成长之旅生成成功！")
                st.session_state["last_journey"] = journey
            except Exception as e:
                friendly_api_error(e)

        # Show last generated journey summary
        last = st.session_state.get("last_journey")
        if last:
            st.markdown("---")
            st.markdown(f"**{last.get('title', '')}**")
            st.caption(last.get("summary", ""))
            insights = last.get("insights", {})
            if insights:
                progress = insights.get("progress_summary", "")
                if progress:
                    st.markdown(f"📈 {progress}")
                next_steps = insights.get("next_step_suggestions", [])
                if next_steps:
                    st.markdown("#### Next Steps" if not is_cn else "#### 下一步建议")
                    for ns in next_steps:
                        st.markdown(f"- {ns}")

    with col_list:
        st.markdown("#### Recent Journeys" if not is_cn else "#### 最近成长之旅")
        try:
            resp = admin_api.list_growth_journeys(member_id=(int(mid) if mid > 0 else None), limit=20)
            items = resp.get("items", [])
            if items:
                for j in items:
                    with st.container(border=True):
                        jid = j.get("id", "")
                        title = j.get("title", "")
                        summary = j.get("summary", "")
                        st.markdown(f"**#{jid} — {title}**")
                        st.caption((summary or "")[:150])
                        if st.button("View Details" if not is_cn else "查看详情",
                                     key=f"view_gj_{jid}"):
                            try:
                                detail = admin_api.get_growth_journey(jid)
                                st.session_state["last_journey"] = detail
                                st.rerun()
                            except Exception as e:
                                friendly_api_error(e)
            else:
                empty_state("🌱", "No Growth Journeys Yet" if not is_cn else "暂无成长之旅",
                            "Generate a journey to turn member records into a timeline." if not is_cn else "生成成长之旅后，成员记录会转化为时间线。")
        except Exception as e:
            friendly_api_error(e)

    # ── Full detail display ──────────────────────────────
    detail = st.session_state.get("last_journey")
    if detail and detail.get("timeline_items"):
        st.markdown("---")
        st.markdown("### 💫 Wellness Timeline" if not is_cn else "### 💫 健康时间线")
        timeline = detail.get("timeline_items", [])
        for i, evt in enumerate(timeline):
            icon = evt.get("icon", "📌")
            date = evt.get("date", "")
            etype = evt.get("event_type", "")
            title = evt.get("title", "")
            desc = evt.get("description", "")

            if etype == "milestone":
                st.markdown(f"""
                <div style="text-align:center;padding:12px;margin:4px 0;">
                    <div style="font-size:13px;font-weight:800;color:var(--brand);letter-spacing:0.08em;text-transform:uppercase;">✨ {title}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-icon">{icon}</div>
                    <div class="timeline-body">
                        <div class="timeline-date">{date[:10] if date else ""}</div>
                        <div class="timeline-title">{title}</div>
                        <div class="timeline-desc">{desc[:200] if desc else ""}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if i < len(timeline) - 1:
                    st.markdown("""
                    <div class="timeline-connector">
                        <div class="timeline-dot"></div>
                        <div class="timeline-line"></div>
                    </div>
                    """, unsafe_allow_html=True)

        insights = detail.get("insights", {})
        if insights:
            st.markdown("---")
            st.markdown("### Insights" if not is_cn else "### 洞察分析")

            emotional = insights.get("emotional_pattern", "")
            if emotional:
                st.markdown(f"**Emotional Pattern:** {emotional}" if not is_cn else f"**情绪模式：**{emotional}")

            challenges = insights.get("key_challenges", [])
            if challenges:
                st.markdown("**Key Challenges**" if not is_cn else "**主要挑战**")
                for c in challenges:
                    st.markdown(f"- {c}")

            actions = insights.get("healing_actions", [])
            if actions:
                st.markdown("**Healing Actions**" if not is_cn else "**康复行动**")
                for a in actions:
                    st.markdown(f"- {a.get('title', '')} ({a.get('status', '')})")

            next_steps = insights.get("next_step_suggestions", [])
            if next_steps:
                st.markdown("**Next Steps**" if not is_cn else "**下一步建议**")
                for ns in next_steps:
                    st.markdown(f"- {ns}")


# ═══════════════════════════════════════════════════
# INSIGHTS — Patterns, Coach, Reflections, Insights Dashboard
# ═══════════════════════════════════════════════════
def render_insights():
    section_header(
        "Insights Dashboard" if not is_cn else "智能洞察",
        "Behaviour patterns, coaching, reflections, and wellness intelligence."
        if not is_cn else "行为模式、健康指导、反思记录和健康智能分析。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    tabs_items = (
        ["📊 Insights", "🔄 Patterns", "🎯 Coach", "📝 Reflections"]
        if not is_cn else
        ["📊 洞察", "🔄 模式", "🎯 指导", "📝 反思"]
    )
    tab_insights, tab_patterns, tab_coach, tab_reflections = st.tabs(tabs_items)

    # ── INSIGHTS TAB ─────────────────────────────────
    with tab_insights:
        st.markdown("#### Generate Member Insights" if not is_cn else "#### 生成成员洞察")
        mid = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="insight_mid")
        if st.button("Generate Insights" if not is_cn else "生成洞察", type="primary", use_container_width=True):
            try:
                data = admin_api.get_insights(member_id=int(mid))
                st.session_state["last_insights"] = data
            except Exception as e:
                friendly_api_error(e)

        last = st.session_state.get("last_insights")
        if last:
            score = last.get("wellness_score")
            if score is not None:
                st.metric("Today's Wellness Score" if not is_cn else "今日健康评分", f"{score}/100")
            trend = last.get("monthly_trend", "")
            if trend:
                st.info(f"📈 {trend}")

            positive = last.get("positive_changes", [])
            if positive:
                st.markdown("**Positive Changes**" if not is_cn else "**积极变化**")
                for p in positive:
                    st.markdown(f"✅ {p}")

            alerts = last.get("risk_alerts", [])
            if alerts:
                st.markdown("**Risk Alerts**" if not is_cn else "**风险警报**")
                for a in alerts:
                    st.markdown(f"⚠️ {a}")

            focus = last.get("recommended_focus", "")
            if focus:
                st.markdown(f"**Recommended Focus:** {focus}" if not is_cn else f"**建议关注：**{focus}")

            achievements = last.get("recent_achievements", [])
            if achievements:
                st.markdown("**Recent Achievements**" if not is_cn else "**近期成就**")
                for a in achievements:
                    st.markdown(f"🏆 {a}")

    # ── PATTERNS TAB ─────────────────────────────────
    with tab_patterns:
        st.markdown("#### Pattern Discovery" if not is_cn else "#### 模式发现")
        mid_p = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="pattern_mid")
        if st.button("Discover Patterns" if not is_cn else "发现模式", type="primary", use_container_width=True):
            try:
                data = admin_api.get_patterns(member_id=int(mid_p))
                patterns = data.get("patterns", [])
                st.session_state["last_patterns"] = patterns
            except Exception as e:
                friendly_api_error(e)

        patterns = st.session_state.get("last_patterns", [])
        if patterns:
            for p in patterns:
                title = p.get("title", "")
                confidence = p.get("confidence", 0)
                evidence = p.get("evidence", "")
                recommendation = p.get("recommendation", "")
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.markdown(f"*Confidence: {confidence*100:.0f}%*" if not is_cn else f"*置信度：{confidence*100:.0f}%*")
                    st.caption(evidence)
                    st.markdown(f"💡 {recommendation}")

    # ── COACH TAB ────────────────────────────────────
    with tab_coach:
        st.markdown("#### Daily Coaching" if not is_cn else "#### 每日健康指导")
        mid_c = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="coach_mid")
        if st.button("Get Daily Message" if not is_cn else "获取每日消息", type="primary", use_container_width=True):
            try:
                msg = admin_api.get_daily_coaching(member_id=int(mid_c))
                st.session_state["last_coach"] = msg
            except Exception as e:
                friendly_api_error(e)

        coach = st.session_state.get("last_coach")
        if coach:
            title = coach.get("title", "")
            content = coach.get("content", "")
            date = coach.get("date", "")
            with st.container(border=True):
                st.markdown(f"### {title}")
                st.caption(date)
                st.markdown(content)

    # ── REFLECTIONS TAB ──────────────────────────────
    with tab_reflections:
        st.markdown("#### Daily Reflection" if not is_cn else "#### 每日反思")
        mid_r = st.number_input("Member ID" if not is_cn else "成员 ID", min_value=1, step=1, key="ref_mid")

        with st.form("reflection_form"):
            went_well = st.text_area("What went well?" if not is_cn else "今天做得好的是什么？")
            challenge = st.text_area("Biggest challenge?" if not is_cn else "最大的挑战？")
            gratitude = st.text_area("Gratitude" if not is_cn else "感恩")
            notes = st.text_area("Notes" if not is_cn else "备注")
            if st.form_submit_button("Save Reflection" if not is_cn else "保存反思", use_container_width=True):
                if not any([went_well.strip(), challenge.strip(), gratitude.strip(), notes.strip()]):
                    st.error("Add at least one reflection note." if not is_cn else "请至少填写一项反思内容。")
                    st.stop()
                try:
                    payload = {"member_id": int(mid_r)}
                    if went_well.strip():
                        payload["went_well"] = went_well.strip()
                    if challenge.strip():
                        payload["biggest_challenge"] = challenge.strip()
                    if gratitude.strip():
                        payload["gratitude"] = gratitude.strip()
                    if notes.strip():
                        payload["notes"] = notes.strip()
                    admin_api.create_reflection(**payload)
                    st.success("Reflection saved!" if not is_cn else "反思保存成功！")
                    st.rerun()
                except Exception as e:
                    friendly_api_error(e)

        st.markdown("---")
        st.markdown("#### Weekly Summary" if not is_cn else "#### 每周总结")
        if st.button("Generate Weekly Summary" if not is_cn else "生成每周总结"):
            try:
                summary = admin_api.get_weekly_reflection_summary(member_id=int(mid_r))
                st.session_state["last_weekly_summary"] = summary
            except Exception as e:
                friendly_api_error(e)

        ws = st.session_state.get("last_weekly_summary")
        if ws:
            with st.container(border=True):
                st.markdown(f"**{ws.get('overall_theme', '')}**")
                themes = ws.get("recurring_themes", [])
                if themes:
                    st.markdown("**Recurring themes:**" if not is_cn else "**重复主题：**")
                    st.markdown(", ".join(themes))
                st.markdown(f"💡 {ws.get('suggestion', '')}")


# ═══════════════════════════════════════════════════
# MEMBER WORKSPACE — unified member hub
# ═══════════════════════════════════════════════════
def render_member_workspace():
    section_header(
        "Member Workspace" if not is_cn else "成员工作区",
        "Everything about one member in one place."
        if not is_cn else "一个成员的所有信息汇聚一处。",
    )
    if not BACKEND or not admin_api:
        empty_state("🔌", "API Not Connected" if not is_cn else "API 未连接", "")
        return

    # ── Member selector ────────────────────────────────
    try:
        members_resp = admin_api.list_members(limit=1000)
        members = members_resp.get("items", [])
    except Exception as e:
        friendly_api_error(e)
        return

    member_options = {f"#{m['id']} — {m['name']}": m for m in members}
    member_names = list(member_options.keys())

    if not member_names:
        empty_state("👥", "No Members Yet" if not is_cn else "暂无成员",
                     "Create a member first to use the workspace." if not is_cn else "请先创建成员，再使用成员工作区。")
        return

    sel_name = st.selectbox(
        "Select Member" if not is_cn else "选择成员",
        member_names,
        key="workspace_member_select",
    )
    member = member_options[sel_name]
    mid = member["id"]

    st.markdown("---")

    # ── Workspace Tabs ─────────────────────────────────
    tab_labels = (
        ["Overview", "Timeline", "AI Reports", "Healing Plans", "Reflections", "Growth Journey"]
        if not is_cn
        else ["概览", "时间线", "AI 报告", "康复计划", "反思", "成长之旅"]
    )
    tabs = st.tabs(tab_labels)

    # ── TAB: Overview ──────────────────────────────────
    with tabs[0]:
        st.markdown(f"### {member['name']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Age:** {member.get('age', '—')}")
            st.markdown(f"**Gender:** {member.get('gender', '—')}")
        with col2:
            st.markdown(f"**Country:** {member.get('country', '—')}")
            st.markdown(f"**Language:** {member.get('preferred_language', '—')}")
        with col3:
            created = (member.get("created_at") or "")[:10]
            st.markdown(f"**Member since:** {created}")

        st.markdown("---")
        mname = member["name"]
        mage = member.get("age", 30)

        # Quick insights summary
        st.markdown(f"**Member Profile:** {mname} ({'Age' if not is_cn else '年龄'}: {mage})")
        try:
            ins = admin_api.get_insights(member_id=mid)
            score = ins.get("wellness_score")
            if score is not None:
                st.metric("Wellness Score" if not is_cn else "健康评分", f"{score}/100")
            focus = ins.get("recommended_focus", "")
            if focus:
                st.info(f"🎯 {focus}")
        except Exception:
            st.info("No insights yet." if not is_cn else "暂无洞察数据。")

    # ── TAB: Timeline (visual chronological flow) ──
    with tabs[1]:
        st.markdown("### Timeline" if not is_cn else "### 时间线")
        try:
            journeys = admin_api.list_growth_journeys(member_id=mid, limit=1)
            journey_items = journeys.get("items", [])
            if journey_items:
                latest_id = journey_items[0].get("id")
                gj = admin_api.get_growth_journey(latest_id) if latest_id else journey_items[0]
                timeline = gj.get("timeline_items", [])
            else:
                timeline = []
        except Exception as e:
            friendly_api_error(e)
            timeline = []

        if timeline:
            for i, evt in enumerate(timeline):
                icon = evt.get("icon", "📌")
                date = evt.get("date", "")
                title = evt.get("title", "")
                desc = evt.get("description", "")
                etype = evt.get("event_type", "")

                if etype == "milestone":
                    st.markdown(f"""
                    <div style="text-align:center;padding:12px;margin:4px 0;">
                        <div style="font-size:13px;font-weight:800;color:var(--brand);letter-spacing:0.08em;text-transform:uppercase;">
                            ✨ {title}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="timeline-item">
                        <div class="timeline-icon">{icon}</div>
                        <div class="timeline-body">
                            <div class="timeline-date">{date[:10] if date else ""}</div>
                            <div class="timeline-title">{title}</div>
                            <div class="timeline-desc">{desc[:200] if desc else ""}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if i < len(timeline) - 1:
                        st.markdown("""
                        <div class="timeline-connector">
                            <div class="timeline-dot"></div>
                            <div class="timeline-line"></div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            empty_state("🕒", "No Timeline Yet" if not is_cn else "暂无时间线",
                        "Generate a Growth Journey to create a member timeline." if not is_cn else "生成成长之旅后，这里会显示成员时间线。")

    # ── TAB: AI Reports ────────────────────────────
    with tabs[2]:
        try:
            reports = admin_api.list_ai_reports(limit=50)
            items = [r for r in reports.get("items", []) if r.get("member_id") == mid]
            if items:
                for r in items:
                    with st.container(border=True):
                        st.markdown(f"**Report #{r['id']}** — {status_badge(r.get('risk_level', 'N/A'))}")
                        summary = r.get("summary", "") or ""
                        st.caption(summary[:200])
            else:
                empty_state("📊", "No AI Reports Yet" if not is_cn else "暂无 AI 报告",
                            "Generate an AI report for this member." if not is_cn else "为该成员生成 AI 报告后将在这里显示。")
        except Exception as e:
            friendly_api_error(e)

    # ── TAB: Healing Plans ─────────────────────────
    with tabs[3]:
        try:
            plans = admin_api.list_healing_plans(limit=50)
            items = [p for p in plans.get("items", []) if p.get("member_id") == mid]
            if items:
                for p in items:
                    with st.container(border=True):
                        st.markdown(f"**{p['title']}** {status_badge(p.get('status', 'active'))}")
                        if p.get("description"):
                            st.caption(p["description"][:200])
            else:
                empty_state("🎯", "No Healing Plans Yet" if not is_cn else "暂无康复计划",
                            "Create a healing plan to track care actions." if not is_cn else "创建康复计划后可在这里跟踪行动。")
        except Exception as e:
            friendly_api_error(e)

    # ── TAB: Reflections ───────────────────────────
    with tabs[4]:
        try:
            refs = admin_api.list_reflections(member_id=mid, limit=50)
            items = refs.get("items", [])
            if items:
                for ref in items:
                    with st.container(border=True):
                        went = ref.get("went_well", "")
                        challenge = ref.get("biggest_challenge", "")
                        date_ref = (ref.get("created_at") or "")[:10]
                        st.markdown(f"**{date_ref}**")
                        if went:
                            st.markdown(f"✅ {went}")
                        if challenge:
                            st.markdown(f"⚠️ {challenge}")
            else:
                empty_state("📝", "No Reflections Yet" if not is_cn else "暂无反思记录",
                            "Create reflections to capture member progress." if not is_cn else "创建反思记录后可在这里查看成长线索。")
        except Exception as e:
            friendly_api_error(e)

        st.markdown("---")
        if st.button("Generate Weekly Summary" if not is_cn else "生成每周总结"):
            try:
                ws = admin_api.get_weekly_reflection_summary(member_id=mid)
                st.session_state["ws_workspace"] = ws
            except Exception as e:
                friendly_api_error(e)
        ws = st.session_state.get("ws_workspace")
        if ws:
            with st.container(border=True):
                st.markdown(f"**{ws.get('overall_theme', '')}**")
                themes = ws.get("recurring_themes", [])
                if themes:
                    st.markdown(", ".join(themes))
                if ws.get("suggestion"):
                    st.markdown(f"💡 {ws.get('suggestion')}")

    # ── TAB: Growth Journey ────────────────────────
    with tabs[5]:
        if st.button("Generate Growth Journey" if not is_cn else "生成成长之旅", type="primary"):
            try:
                gj = admin_api.generate_growth_journey(member_id=mid)
                st.session_state["gj_workspace"] = gj
            except Exception as e:
                friendly_api_error(e)

        gj = st.session_state.get("gj_workspace")
        if gj:
            st.markdown(f"### {gj.get('title', '')}")
            st.caption(gj.get("summary", ""))

            insights = gj.get("insights", {})
            if insights:
                st.markdown("#### Insights" if not is_cn else "#### 洞察")
                emotional = insights.get("emotional_pattern", "")
                if emotional:
                    st.markdown(f"💭 {emotional}")
                next_steps = insights.get("next_step_suggestions", [])
                if next_steps:
                    st.markdown("**Next Steps**" if not is_cn else "**下一步**")
                    for ns in next_steps:
                        st.markdown(f"- {ns}")
        else:
            empty_state("🌱", "No Growth Journey Selected" if not is_cn else "暂无成长之旅",
                        "Generate a Growth Journey to see member insights and next steps." if not is_cn else "生成成长之旅后，这里会显示成员洞察和下一步建议。")


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
    "Growth Journey": render_growth_journey,
    "Insights": render_insights,
    "Member Workspace": render_member_workspace,
}

render_fn = PAGE_RENDERERS.get(page_key, render_dashboard)
render_fn()
