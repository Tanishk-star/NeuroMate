"""
pages/Insights.py — NeuroMate Insights Page
=============================================
Productivity analytics and AI-generated insights.

Planned features:
    - Task completion rate over time.
    - Priority distribution breakdown.
    - Mood trend from journal data.
    - Weekly productivity score.
    - Agent recommendation effectiveness.

Currently shows placeholder charts and metrics with live task data
where available.
"""

import streamlit as st
from datetime import datetime, date, timedelta

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server as mcp
from config import APP_NAME
from utils import apply_custom_theme

# Apply page configuration and design system
apply_custom_theme(f"Insights — {APP_NAME}", "📊")


# ─── Helper (defined before use) ──────────────────────────────────────────────
def _placeholder_chart(title: str, message: str):
    """Render a consistent placeholder when no data is available."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align:center; padding: 2rem 1rem;">
                <div style="font-size: 2rem;">📊</div>
                <p style="font-weight: 600;">{title}</p>
                <p style="color: #9ca3af; font-size: 0.85rem;">{message}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1 class="page-title">📊 Insights & Analytics</h1>
        <p class="page-subtitle">Understand your daily patterns and improve week over week with AI analytics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Live Metrics ─────────────────────────────────────────────────────────────
all_tasks = mcp.get_tasks()
pending = [t for t in all_tasks if t.status == "pending"]
completed = [t for t in all_tasks if t.status == "completed"]
in_progress = [t for t in all_tasks if t.status == "in_progress"]
high_priority = [t for t in all_tasks if t.priority == "high"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Total Tasks", len(all_tasks))
with col2:
    rate = round(len(completed) / max(len(all_tasks), 1) * 100)
    st.metric("✅ Completion Rate", f"{rate}%")
with col3:
    st.metric("🔴 High Priority", len(high_priority))
with col4:
    st.metric("🔄 In Progress", len(in_progress))

st.divider()

# ─── Chart Placeholders ───────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    # ── Task Status Breakdown ──────────────────────────────────────────────
    st.subheader("📌 Task Status Breakdown")
    if all_tasks:
        import pandas as pd
        # compute overdue vs upcoming
        now = datetime.now()
        upcoming = 0
        overdue = 0
        for t in all_tasks:
            if t.status in ["pending", "in_progress"]:
                if t.due_date:
                    try:
                        due_dt = datetime.fromisoformat(t.due_date)
                        if due_dt.date() < now.date():
                            overdue += 1
                        else:
                            upcoming += 1
                    except ValueError:
                        upcoming += 1
                else:
                    upcoming += 1
                    
        status_data = {
            "Status": ["Completed", "In Progress", "Upcoming", "Overdue"],
            "Count": [len(completed), len(in_progress), upcoming, overdue],
        }
        df_status = pd.DataFrame(status_data)
        st.bar_chart(df_status.set_index("Status"), color="#6366f1", height=300)
    else:
        _placeholder_chart("Task Status Breakdown", "Add tasks to see your breakdown")

    # ── Priority Distribution ──────────────────────────────────────────────
    st.subheader("🎯 Priority Distribution")
    if all_tasks:
        import pandas as pd
        priority_data = {
            "Priority": ["High", "Medium", "Low"],
            "Count": [
                len([t for t in all_tasks if t.priority == "high"]),
                len([t for t in all_tasks if t.priority == "medium"]),
                len([t for t in all_tasks if t.priority == "low"]),
            ],
        }
        df_priority = pd.DataFrame(priority_data)
        st.bar_chart(df_priority.set_index("Priority"), color="#10b981", height=260)
    else:
        _placeholder_chart("Priority Distribution", "Add tasks to see priorities")

with right:
    # ── Weekly Activity ────────────────────────────────────────
    st.subheader("📅 Weekly Progress")
    if all_tasks:
        import pandas as pd
        import random
        days = [(date.today() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        # Simulated weekly progress based on completed tasks
        completions = [random.randint(0, 3) for _ in range(6)] + [len(completed)]
        df_weekly = pd.DataFrame({"Day": days, "Completed Tasks": completions})
        st.line_chart(df_weekly.set_index("Day"), color="#f59e0b", height=260)
        
        score = min(100, int((len(completed) / max(len(all_tasks), 1)) * 100) + (len(high_priority)*5))
        st.markdown(f"**Productivity Score:** {score}/100")
        st.progress(score / 100)
    else:
        _placeholder_chart("Weekly Progress", "Add and complete tasks to see trends")

    # ── Mood Trend ─────────────────────────────────────────────
    st.subheader("🧘 Mood Trend")
    # Simulated mood data if no journal entries
    if all_tasks:
        import pandas as pd
        import random
        moods = ["Neutral", "Good", "Great", "Good", "Neutral", "Low", "Good"]
        days = [(date.today() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        st.line_chart(pd.DataFrame({"Mood Score": [3, 4, 5, 4, 3, 2, 4]}, index=days), color="#ec4899", height=200)
    else:
        _placeholder_chart("Mood Trend Analysis", "Start journaling to track mood patterns")

# ─── AI Insights ──────────────────────────────────────────────────
st.divider()
st.subheader("🤖 AI-Generated Insights")
if all_tasks:
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="padding: 1rem;">
                <p><strong>Insight 1:</strong> You have {len(completed)} completed tasks. Keep up the good work!</p>
                <p><strong>Insight 2:</strong> With {len(high_priority)} high priority tasks, consider tackling the hardest ones early in the day.</p>
                <p><strong>Insight 3:</strong> A short break could help maintain your momentum.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    with st.container(border=True):
        st.markdown(
            """
            <div style="text-align:center; padding: 1.5rem 1rem;">
                <div style="font-size: 2.5rem;">🔍</div>
                <p style="font-weight: 600; margin-top: 0.5rem;">
                    No tasks yet
                </p>
                <p style="color: #9ca3af; font-size: 0.875rem; max-width: 500px; margin: auto;">
                    Add tasks to the planner to receive personalized insights and recommendations.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )



