import streamlit as st
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server as mcp
from utils import today_label, init_session_key, apply_custom_theme
from config import APP_NAME

# Apply page configuration and design system
apply_custom_theme(f"Dashboard — {APP_NAME}", "🧠")

# ─── Session State ────────────────────────────────────────────────────────────
init_session_key("user_name", "Friend")

# ─── Dynamic Greeting ─────────────────────────────────────────────────────────
hour = datetime.now().hour
if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="padding: 1rem 0 1.5rem 0;">
        <span style="color:#818cf8; font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
            👋 {greeting}, {st.session_state.user_name}
        </span>
        <h1 style="margin: 0.25rem 0 0 0; font-size: 2.8rem; font-weight: 800; letter-spacing: -0.04em; background: linear-gradient(90deg, #ffffff, #9ca3af); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            NeuroMate
        </h1>
        <p style="color: #64748b; font-size: 1.05rem; margin-top: 0.25rem; font-weight: 500;">
            Your AI Daily Decision Companion &nbsp;·&nbsp; <span style="color:#475569;">Focus on what matters today.</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Fetch Data ───────────────────────────────────────────────────────────────
tasks = mcp.get_tasks()
pending_tasks = [t for t in tasks if t.status == "pending"]
completed_tasks = [t for t in tasks if t.status == "completed"]
today_str = datetime.now().date().isoformat()
today_events = mcp.get_events(date=today_str)

# ─── Quick Stats Row ──────────────────────────────────────────────────────────
# Calculate counts
tasks_count = len(pending_tasks)
events_count = len(today_events)

# Render HTML Grid for Stats
st.markdown(
    f"""
    <div class="stat-card-container">
        <div class="stat-card">
            <div class="stat-card-title">📋 Today's Tasks</div>
            <div class="stat-card-value">{tasks_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-title">📅 Events Scheduled</div>
            <div class="stat-card-value">{events_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-title">⚡ Focus Score</div>
            <div class="stat-card-value" style="background: linear-gradient(90deg, #818cf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">88/100</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-title">🔋 Energy Level</div>
            <div class="stat-card-value" style="color: #10b981;">Optimal</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ─── Main Content Columns ─────────────────────────────────────────────────────
left, right = st.columns([1.5, 1], gap="large")

with left:
    # ── AI Recommendation Card ─────────────────────────────────────────────
    st.markdown(
        """
        <div class="rec-card">
            <div style="display: flex; align-items: flex-start; gap: 16px;">
                <div style="font-size: 2.5rem; line-height: 1; filter: drop-shadow(0 0 10px rgba(99,102,241,0.5));">🤖</div>
                <div>
                    <h4 style="margin: 0 0 4px 0; color: #a5b4fc; font-weight: 700; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 0.05em;">AI Companion Recommendation</h4>
                    <p style="margin: 0; font-size: 0.95rem; color: #e5e7eb; line-height: 1.5; font-weight: 400;">
                        "Based on today's workload, begin with your highest-priority assignment before noon. Schedule a 15-minute break after 90 minutes of focused work."
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Upcoming Tasks ─────────────────────────────────────────────────────
    st.subheader("📋 Upcoming Tasks")
    
    if pending_tasks:
        priority_display = {"high": "High", "medium": "Medium", "low": "Low"}
        for task in pending_tasks[:5]:  # Show top 5
            badge_class = f"badge-{task.priority}"
            priority_lbl = priority_display.get(task.priority, "Medium")
            due_lbl = f"Due: {task.due_date}" if task.due_date else "No due date"
            
            with st.container(border=True):
                col_check, col_title, col_details = st.columns([0.4, 5, 2.2])
                with col_check:
                    is_completed = st.checkbox("", key=f"complete_{task.id}", value=False)
                    if is_completed:
                        mcp.update_task(task.id, status="completed")
                        st.success(f"✓ Task completed!")
                        st.rerun()
                with col_title:
                    st.markdown(f"<div style='font-weight:600; font-size:0.95rem;'>{task.title}</div>", unsafe_allow_html=True)
                    if task.description:
                        st.caption(task.description[:80])
                with col_details:
                    st.markdown(
                        f"""
                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                            <span class="task-badge {badge_class}">{priority_lbl}</span>
                            <span style="font-size: 0.75rem; color: #64748b; font-weight:500;">{due_lbl} &nbsp;·&nbsp; 45m</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        if len(pending_tasks) > 5:
            st.markdown(
                f"""
                <div style="text-align: center; padding-top: 8px;">
                    <a href="Planner" target="_self" style="color: #818cf8; font-size: 0.85rem; font-weight: 600; text-decoration: none;">
                        + View all {len(pending_tasks)} tasks in Planner
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No pending tasks. Head to the Planner to add tasks!", icon="📝")

with right:
    # ── Today's Schedule (Timeline) ─────────────────────────────────────────
    st.subheader("📅 Today's Schedule")
    
    st.markdown(
        """
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-time">8:00 AM</div>
                <div class="timeline-content">
                    <strong style="color: #e5e7eb; font-size: 0.9rem;">Planning Block</strong>
                    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #9ca3af; line-height: 1.4;">
                        Set priorities, align goals, and review task queue with Intake Agent.
                    </p>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-time">10:30 AM</div>
                <div class="timeline-content">
                    <strong style="color: #e5e7eb; font-size: 0.9rem;">Deep Work Session</strong>
                    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #9ca3af; line-height: 1.4;">
                        High-priority project focus. Minimize interruptions.
                    </p>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-time">1:00 PM</div>
                <div class="timeline-content">
                    <strong style="color: #e5e7eb; font-size: 0.9rem;">Focus Session</strong>
                    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #9ca3af; line-height: 1.4;">
                        Review task priority queue and administrative details.
                    </p>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-time">4:00 PM</div>
                <div class="timeline-content">
                    <strong style="color: #e5e7eb; font-size: 0.9rem;">Wrap-up & Reflect</strong>
                    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #9ca3af; line-height: 1.4;">
                        Self-reflection, journal logging, and next-day pre-planning.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Quick Actions ────────────────────────────────────────────────────────────
st.divider()
st.subheader("⚡ Quick Actions")

q1, q2, q3, q4 = st.columns(4)
with q1:
    if st.button("➕ Add Task", use_container_width=True):
        st.switch_page("pages/Planner.py")
with q2:
    if st.button("🗓 Schedule Event", use_container_width=True):
        st.switch_page("pages/Planner.py")
with q3:
    if st.button("💬 Open Companion", use_container_width=True):
        st.switch_page("pages/Companion.py")
with q4:
    if st.button("📓 Write in Journal", use_container_width=True):
        st.switch_page("pages/Journal.py")

