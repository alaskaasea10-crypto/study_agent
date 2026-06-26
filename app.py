from __future__ import annotations

import html
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


st.set_page_config(page_title="学伴 Study Agent", page_icon="Study", layout="wide")


def safe_text(value: Any, fallback: str = "暂无") -> str:
    if value is None:
        return fallback
    if isinstance(value, (list, dict)):
        return fallback
    text = str(value).strip()
    return text or fallback


def item_text(value: Any) -> str:
    if isinstance(value, dict):
        return "；".join(f"{key}：{item_text(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "；".join(item_text(item) for item in value)
    return safe_text(value)


def items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item_text(item) for item in value]
    if isinstance(value, dict):
        return [f"{key}：{item_text(item)}" for key, item in value.items()]
    return [safe_text(value)]


def esc(value: Any) -> str:
    return html.escape(safe_text(value))


def display_time(value: Any) -> str:
    text = safe_text(value).replace("T", " ")
    return text[:16] if len(text) >= 16 else text


def list_html(values: list[str]) -> str:
    if not values:
        return '<p class="muted">暂无内容</p>'
    return "<ul>" + "".join(f"<li>{html.escape(value)}</li>" for value in values) + "</ul>"


def load_agents() -> dict[str, Any]:
    from study_agent.agents.mistake_analyzer import MistakeAnalysisAgent
    from study_agent.agents.planner import LearningPlanAgent
    from study_agent.agents.summary_agent import LearningSummaryAgent
    from study_agent.memory.storage import JsonMemoryStore
    from study_agent.scheduler.proactive_scheduler import ProactiveScheduler

    memory = JsonMemoryStore()
    return {
        "memory": memory,
        "planner": LearningPlanAgent(memory=memory),
        "mistake_agent": MistakeAnalysisAgent(memory=memory),
        "summary_agent": LearningSummaryAgent(memory=memory),
        "scheduler": ProactiveScheduler(memory=memory),
    }


def render_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #fbfbfa; }
        .block-container {
            max-width: 960px;
            padding-top: 4.2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-bottom: 4rem;
        }
        [data-testid="stSidebar"] {
            background: #f7f7f5;
            border-right: 1px solid #ececea;
        }
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.35 !important;
            font-weight: 680 !important;
            letter-spacing: 0 !important;
            color: #1f1f1f !important;
        }
        .section-title {
            font-size: 1.06rem;
            font-weight: 650;
            color: #303030;
            margin: 1.35rem 0 .7rem;
        }
        .card {
            border: 1px solid #ececea;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            background: #ffffff;
            margin-bottom: .95rem;
            box-shadow: 0 1px 2px rgba(15, 15, 15, .025);
        }
        .plan-card { border-left: 3px solid #6b7cff; }
        .alert-card {
            border-left: 3px solid #d0a85c;
            background: #fffdf8;
        }
        .card-title {
            font-size: .98rem;
            font-weight: 650;
            color: #222222;
            margin-bottom: .35rem;
        }
        .muted {
            color: #5f6368;
            margin: 0;
            line-height: 1.65;
            font-size: .94rem;
        }
        .meta-row {
            display: flex;
            gap: .45rem;
            flex-wrap: wrap;
            margin: .25rem 0 .65rem;
        }
        .tag {
            display: inline-block;
            border-radius: 999px;
            padding: .16rem .5rem;
            background: #f1f3f8;
            color: #465166;
            font-size: .76rem;
            font-weight: 560;
        }
        .time-tag { background: #f0f0ee; color: #5f5f5f; }
        .risk-tag { background: #f8f1e4; color: #7c5d1f; }
        .kv {
            display: grid;
            grid-template-columns: 112px 1fr;
            gap: .45rem .75rem;
            margin: .5rem 0;
        }
        .kv-label { color: #767676; font-weight: 560; font-size: .9rem; }
        .kv-value { color: #303030; font-weight: 560; font-size: .92rem; }
        ul { margin: .35rem 0 0 1.1rem; padding: 0; }
        li { margin: .2rem 0; color: #444444; line-height: 1.55; }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #e1e3e6;
            background: #f3f4f6;
            color: #374151;
            font-weight: 540;
            padding: .55rem .85rem;
            box-shadow: none;
        }
        .stButton > button:hover {
            border-color: #d5d8dd;
            background: #eaecef;
            color: #252b35;
        }
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
            border-radius: 8px;
            border-color: #ddddda;
            background: #ffffff;
        }
        @media (max-width: 760px) {
            .block-container {
                padding-top: 3.5rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .kv { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_note(message: str, alert: bool = False) -> None:
    class_name = "alert-card" if alert else ""
    st.markdown(
        f'<div class="card {class_name}"><p class="muted">{html.escape(message)}</p></div>',
        unsafe_allow_html=True,
    )


def render_reminder_card(card: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="card alert-card">
            <div class="meta-row">
                <span class="tag time-tag">{html.escape(display_time(card.get("created_at")))}</span>
                <span class="tag risk-tag">{esc(card.get("trigger"))}</span>
            </div>
            <div class="card-title">{esc(card.get("title"))}</div>
            <p class="muted">{esc(card.get("message"))}</p>
            <div class="meta-row"><span class="tag">建议动作：{esc(card.get("suggested_action"))}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_plan(result: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">学习计划总览</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("课程", safe_text(result.get("course")))
    col2.metric("考试日期", safe_text(result.get("exam_date")))
    col3.metric("计划天数", f"{len(result.get('daily_plan', []))} 天")

    if result.get("adaptive_reason"):
        render_note(safe_text(result.get("adaptive_reason")))

    risks = items(result.get("risk_alerts"))
    if risks:
        st.markdown('<div class="section-title">风险提醒</div>', unsafe_allow_html=True)
        for risk in risks:
            render_note(risk, alert=True)

    phases = result.get("phases", [])
    if phases:
        st.markdown('<div class="section-title">分阶段复习策略</div>', unsafe_allow_html=True)
        phase_cols = st.columns(min(len(phases), 3))
        for index, phase in enumerate(phases):
            with phase_cols[index % len(phase_cols)]:
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">{esc(phase.get("name"))}</div>
                        <div class="meta-row"><span class="tag">{esc(phase.get("range"))}</span></div>
                        <p class="muted">{esc(phase.get("strategy"))}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="section-title">每日学习卡片</div>', unsafe_allow_html=True)
    for day in result.get("daily_plan", []):
        st.markdown(
            f"""
            <div class="card plan-card">
                <div class="meta-row">
                    <span class="tag time-tag">{html.escape(display_time(day.get("date")))}</span>
                    <span class="tag">{esc(day.get("stage"))}</span>
                    <span class="tag">距考试 {esc(day.get("days_to_exam"))} 天</span>
                </div>
                <div class="card-title">{esc(day.get("theme"))}</div>
                {list_html(items(day.get("tasks")))}
                <div class="kv">
                    <div class="kv-label">建议时长</div>
                    <div class="kv-value">{esc(day.get("duration_hours"))} 小时</div>
                    <div class="kv-label">检查点</div>
                    <div class="kv-value">{esc(day.get("checkpoint"))}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_mistake(result: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">错题分析结果</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card">
            <div class="kv">
                <div class="kv-label">课程</div><div class="kv-value">{esc(result.get("course"))}</div>
                <div class="kv-label">错误类型</div><div class="kv-value">{esc(result.get("error_type"))}</div>
                <div class="kv-label">知识点</div><div class="kv-value">{esc(result.get("knowledge_point"))}</div>
                <div class="kv-label">主要原因</div><div class="kv-value">{esc(result.get("cause"))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">改进建议</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card plan-card">{list_html(items(result.get("review_advice")))}</div>', unsafe_allow_html=True)
    if result.get("next_practice"):
        st.markdown('<div class="section-title">下次练习策略</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{list_html(items(result.get("next_practice")))}</div>', unsafe_allow_html=True)
    if result.get("proactive_alert"):
        render_note(safe_text(result.get("proactive_alert")), alert=True)


def render_summary(result: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">今日学习总结</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card plan-card"><div class="card-title">总结</div><p class="muted">{esc(result.get("summary"))}</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section-title">问题分析</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{list_html(items(result.get("problem_analysis")))}</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-title">明日建议</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{list_html(items(result.get("tomorrow_suggestions")))}</div>', unsafe_allow_html=True)
    if result.get("memory_update_hint"):
        render_note(safe_text(result.get("memory_update_hint")))
    if result.get("proactive_follow_up"):
        render_note(safe_text(result.get("proactive_follow_up")))


def render_memory(memory: Any) -> None:
    data = memory.load()
    mistakes = data.get("mistakes", [])
    records = data.get("study_records", [])
    plans = data.get("plans", [])
    events = data.get("scheduler_events", [])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("错题记忆", f"{len(mistakes)} 条")
    col2.metric("学习总结", f"{len(records)} 条")
    col3.metric("学习计划", f"{len(plans)} 个")
    col4.metric("主动提醒", f"{len(events)} 次")

    st.markdown('<div class="section-title">薄弱点排行</div>', unsafe_allow_html=True)
    weak_points = memory.weak_points()
    if weak_points:
        for point in weak_points:
            st.markdown(
                f"""
                <div class="card">
                    <div class="meta-row">
                        <span class="tag">{esc(point.get("knowledge_point"))}</span>
                        <span class="tag risk-tag">出现 {esc(point.get("count"))} 次</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        render_note("暂未记录薄弱点。录入错题后，系统会自动生成知识点排行。")

    st.markdown('<div class="section-title">最近学习总结</div>', unsafe_allow_html=True)
    if records:
        for record in reversed(records[-5:]):
            st.markdown(
                f"""
                <div class="card">
                    <div class="meta-row"><span class="tag time-tag">{html.escape(display_time(record.get("created_at")))}</span></div>
                    <p class="muted">{esc(record.get("summary"))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        render_note("暂无学习总结。")


def main() -> None:
    render_style()
    st.title("学伴 Study Agent")
    st.caption("面向大学生的主动服务型学习 AI Agent 系统")

    try:
        modules = load_agents()
    except Exception as exc:
        st.write("系统已启动，但部分模块未加载。")
        st.exception(exc)
        return

    memory = modules["memory"]
    planner = modules["planner"]
    mistake_agent = modules["mistake_agent"]
    summary_agent = modules["summary_agent"]
    scheduler = modules["scheduler"]

    with st.sidebar:
        st.markdown("### 学伴导航")
        page = st.radio(
            "功能",
            ["学习计划", "错题分析", "学习总结", "记忆中心"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("### 主动提醒")
        if st.button("模拟一天提醒"):
            st.session_state["cards"] = scheduler.generate_cards(simulate=True)
        for card in st.session_state.get("cards", []):
            render_reminder_card(card)
        if not st.session_state.get("cards"):
            st.caption("点击按钮后，系统会模拟晨间、午间、晚间主动服务。")

    if page == "学习计划":
        st.markdown('<div class="section-title">生成学习计划</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.3, 1, 1])
        course = col1.text_input("课程", value="高等数学")
        exam_date = col2.date_input("考试日期")
        daily_hours = col3.number_input("每日学习时长", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
        if st.button("生成自适应学习计划"):
            st.session_state["plan_result"] = planner.generate(course, exam_date.isoformat(), float(daily_hours))
        if st.session_state.get("plan_result"):
            render_plan(st.session_state["plan_result"])
        else:
            render_note("输入课程和考试日期后，生成一份会参考错题记忆的学习计划。")

    elif page == "错题分析":
        st.markdown('<div class="section-title">分析错题</div>', unsafe_allow_html=True)
        course = st.text_input("错题课程", value="高等数学")
        description = st.text_area("错题描述", height=140, placeholder="例如：极限题中等价无穷小条件判断错误...")
        if st.button("分析并写入错题记忆"):
            st.session_state["mistake_result"] = mistake_agent.analyze(description=description, course=course)
        if st.session_state.get("mistake_result"):
            render_mistake(st.session_state["mistake_result"])
        else:
            render_note("录入错题后，系统会识别错误类型、知识点，并给出后续练习策略。")

    elif page == "学习总结":
        st.markdown('<div class="section-title">生成学习总结</div>', unsafe_allow_html=True)
        content = st.text_area("今日学习内容", height=140, placeholder="例如：复习了导数定义，完成 20 道练习...")
        if st.button("生成今日总结"):
            st.session_state["summary_result"] = summary_agent.summarize(content)
        if st.session_state.get("summary_result"):
            render_summary(st.session_state["summary_result"])
        else:
            render_note("记录今日学习内容后，系统会生成总结、问题分析和明日建议。")

    else:
        st.markdown('<div class="section-title">记忆中心</div>', unsafe_allow_html=True)
        render_memory(memory)


if __name__ == "__main__":
    main()
