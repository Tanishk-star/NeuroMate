"""
pages/Planner.py — NeuroMate Planner Page
==========================================
Allows users to manually add and manage tasks and events.
Provides a placeholder "Generate AI Plan" button for future use.

Sections:
    - Add Task form
    - Add Event form
    - Current task list with delete
    - Generate Plan CTA (placeholder)
"""

import streamlit as st
from datetime import datetime, date

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server as mcp
from config import APP_NAME
from utils import apply_css_only

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1 class="page-title">🗓 Daily Planner</h1>
        <p class="page-subtitle">Add tasks and events, then let your AI agents build the perfect schedule.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Layout ───────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ──────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN — Add Task
# ──────────────────────────────────────────────────────────────────────────────
with left:
    st.subheader("➕ Add a Task")

    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input(
            "Task Title *",
            placeholder="e.g. Finish project proposal",
            max_chars=120,
        )
        task_description = st.text_area(
            "Description",
            placeholder="Optional — add context or acceptance criteria.",
            height=80,
        )
        task_col1, task_col2 = st.columns(2)
        with task_col1:
            task_priority = st.selectbox(
                "Priority",
                options=["high", "medium", "low"],
                index=1,
            )
        with task_col2:
            task_due = st.date_input(
                "Due Date",
                value=None,
                min_value=date.today(),
                format="MM/DD/YYYY",
            )
        task_tags_raw = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g. work, health, learning",
        )

        submitted_task = st.form_submit_button("Save Task", use_container_width=True)

        if submitted_task:
            if not task_title.strip():
                st.error("Task title is required.")
            else:
                tags = [t.strip() for t in task_tags_raw.split(",") if t.strip()]
                due_str = task_due.isoformat() if task_due else None
                mcp.add_task(
                    title=task_title.strip(),
                    description=task_description.strip(),
                    priority=task_priority,
                    due_date=due_str,
                    tags=tags,
                )
                st.success(f"✅ Task **'{task_title}'** added successfully!")
                st.rerun()

    # ── Generate Plan ──────────────────────────────────────────────
    st.divider()
    st.subheader("🤖 Your Daily Schedule")
    
    tasks = mcp.get_tasks()
    today_str = date.today().isoformat()
    # Assume today's tasks are those due today or with no due date
    today_tasks = [t for t in tasks if not t.due_date or t.due_date <= today_str]
    future_tasks = [t for t in tasks if t.due_date and t.due_date > today_str and t.status != "completed"]

    if not today_tasks:
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align:center; padding: 1rem;">
                    <div style="font-size: 2rem;">🗓</div>
                    <p style="font-weight: 600;">No tasks yet</p>
                    <p style="color: #9ca3af; font-size: 0.85rem;">
                        Add some tasks above to generate a realistic time-blocked schedule.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        # Generate a simulated time-blocked schedule
        # Start from 8:00 AM and allocate 1 hour per task with 15 min breaks
        import datetime as dt
        current_time = dt.datetime.combine(dt.date.today(), dt.time(8, 0))
        
        timeline_html = '<div class="timeline">'
        for task in today_tasks:
            time_str = current_time.strftime("%I:%M %p").lstrip("0")
            
            timeline_html += f'''
            <div class="timeline-item">
                <div class="timeline-time">{time_str}</div>
                <div class="timeline-content">
                    <div style="font-weight: 600;">{task.title}</div>
                    <div style="font-size: 0.85rem; color: #9ca3af; margin-top: 4px;">{task.description if task.description else "Focused work block"}</div>
                </div>
            </div>
            '''
            # advance time by 1 hour
            current_time += dt.timedelta(hours=1)
            
            # add break
            break_time_str = current_time.strftime("%I:%M %p").lstrip("0")
            timeline_html += f'''
            <div class="timeline-item">
                <div class="timeline-time">{break_time_str}</div>
                <div class="timeline-content" style="border-left: 2px solid #10b981;">
                    <div style="font-weight: 600; color: #10b981;">Short Break</div>
                </div>
            </div>
            '''
            current_time += dt.timedelta(minutes=15)
            
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)

    # ── Upcoming Tasks ─────────────────────────────────────────────
    st.divider()
    st.subheader("📌 Upcoming Tasks")
    
    if future_tasks:
        # Sort by due date (earliest first)
        future_tasks.sort(key=lambda t: t.due_date)
        for task in future_tasks:
            # Format the due date to MM/DD/YYYY if possible
            try:
                dt_obj = datetime.strptime(task.due_date, "%Y-%m-%d")
                formatted_due = dt_obj.strftime("%m/%d/%Y")
            except Exception:
                formatted_due = task.due_date
                
            with st.container(border=True):
                st.markdown(f"**{task.title}**")
                st.caption(f"Due: {formatted_due} | Priority: {task.priority.capitalize()}")
    else:
        st.info("No upcoming tasks. You're all caught up!")

# ──────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN — Add Event & Task List
# ──────────────────────────────────────────────────────────────────────────────
with right:
    st.subheader("🗓 Add an Event")

    with st.form("add_event_form", clear_on_submit=True):
        event_title = st.text_input(
            "Event Title *",
            placeholder="e.g. Team standup",
            max_chars=120,
        )
        event_description = st.text_area(
            "Description",
            placeholder="Optional event details.",
            height=60,
        )
        ev_col1, ev_col2 = st.columns(2)
        with ev_col1:
            event_date = st.date_input("Date *", value=date.today(), format="MM/DD/YYYY")
            event_start = st.time_input("Start Time *", value=datetime.now().time())
        with ev_col2:
            event_location = st.text_input("Location", placeholder="Room / Zoom link")
            event_end = st.time_input("End Time *")

        event_type = st.selectbox(
            "Event Type",
            options=["meeting", "personal", "health", "other"],
            index=0,
        )

        submitted_event = st.form_submit_button("Save Event", use_container_width=True)

        if submitted_event:
            if not event_title.strip():
                st.error("Event title is required.")
            else:
                start_iso = datetime.combine(event_date, event_start).isoformat()
                end_iso = datetime.combine(event_date, event_end).isoformat()
                mcp.add_event(
                    title=event_title.strip(),
                    start_time=start_iso,
                    end_time=end_iso,
                    description=event_description.strip(),
                    location=event_location.strip(),
                    event_type=event_type,
                )
                st.success(f"✅ Event **'{event_title}'** added!")
                st.rerun()

    # ── Current Task List ─────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 All Tasks")
    tasks = mcp.get_tasks()

    if tasks:
        priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        status_icons = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}

        for task in tasks:
            with st.container(border=True):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    p_icon = priority_icons.get(task.priority, "⚪")
                    s_icon = status_icons.get(task.status, "⚪")
                    st.markdown(f"**{p_icon} {task.title}** &nbsp; {s_icon} `{task.status}`")
                    if task.due_date:
                        st.caption(f"📆 Due: {task.due_date}")
                with col_del:
                    if st.button("🗑", key=f"del_{task.id}", help="Delete this task"):
                        mcp.delete_task(task.id)
                        st.rerun()
    else:
        st.info("No tasks yet. Add your first one using the form!", icon="📝")
