"""
app.py — NeuroMate Main Application Entry Point
=================================================
Run with: streamlit run app.py

This file configures the Streamlit multi-page application:
    - Sets the global page configuration and theme.
    - Defines the sidebar navigation.
    - Displays the landing/home screen.
    - Initialises global session state.
    - Shows a configuration warning if secrets are missing.

Architecture Note:
    Each page in the pages/ directory is a separate Streamlit script.
    Streamlit's native multi-page routing handles navigation automatically.
    This file serves as the root that users land on when the app starts.
"""

import streamlit as st
import sys
import os

# Ensure project root is on the Python path for clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from utils import today_label, init_session_key, apply_custom_theme

# Apply visual design system and page configuration
apply_custom_theme(APP_NAME, "🧠")

# ─── Global Session State Initialization ──────────────────────────────────────
init_session_key("user_name", "Friend")
init_session_key("chat_history", [])
init_session_key("journal_authenticated", False)
init_session_key("pipeline_results", {})

# ─── Sidebar Layout ───────────────────────────────────────────────────────────
with st.sidebar:
    # Big logo & Title
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="font-size: 3.5rem; text-shadow: 0 0 15px rgba(99,102,241,0.3); margin-bottom: 0.5rem;">🧠</div>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.04em; color: #ffffff;">
                {APP_NAME}
            </h2>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0.25rem 0 0 0; font-weight: 500;">
                {APP_DESCRIPTION}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Time Info
    st.markdown(
        f"""
        <div style="padding: 0.2rem 1rem;">
            <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:600; letter-spacing:0.05em;">Today</span>
            <p style="margin:0; font-size:0.9rem; font-weight:500; color:#e5e7eb;">{today_label()}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Profile Area
    user_initial = st.session_state.user_name[0].upper() if st.session_state.user_name else "U"
    st.markdown(
        f"""
        <div class="sidebar-profile">
            <div class="profile-avatar">{user_initial}</div>
            <div class="profile-info">
                <span class="profile-name">{st.session_state.user_name}</span>
                <span class="profile-status">
                    <span class="profile-status-dot"></span>
                    System Active
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        f"<p style='color:#475569; font-size:0.7rem; text-align:center; margin-top:1rem;'>v{APP_VERSION} · built for kaggle ai capstone</p>",
        unsafe_allow_html=True,
    )

# ─── Home / Landing Screen ────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align: center; padding: 3rem 2rem 2rem 2rem;">
        <div style="font-size: 5rem; margin-bottom: 1rem;">🧠</div>
        <h1 style="font-size: 2.75rem; font-weight: 800; margin: 0;">
            Welcome to {APP_NAME}
        </h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-top: 0.75rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            {APP_DESCRIPTION}
        </p>
        <p style="color: #94a3b8; margin-top: 0.5rem;">
            Reduce decision fatigue. Reclaim your focus. Let AI do the heavy lifting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ─── Feature Overview Cards ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="medium")

features = [
    ("📋", "Smart Task Management", "Add and organise tasks. AI agents prioritise them by urgency and importance."),
    ("🗓", "Intelligent Scheduling", "Time-block your day automatically based on your priorities and energy levels."),
    ("🧘", "Wellness Monitoring", "Get nudged to take breaks, hydrate, and avoid burnout before it happens."),
    ("💡", "Personalised Recommendations", "Context-aware suggestions tailored to your goals and personality."),
    ("📓", "Private Journal", "A secure, password-protected diary to capture your thoughts and track mood trends."),
    ("📊", "Productivity Insights", "Understand your patterns and improve week over week with AI analytics."),
]

for i, (icon, title, desc) in enumerate(features):
    with [col1, col2, col3][i % 3]:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.5rem 0;">
                    <div style="font-size: 1.75rem;">{icon}</div>
                    <p style="font-weight: 600; margin: 0.4rem 0 0.25rem 0;">{title}</p>
                    <p style="color: #64748b; font-size: 0.85rem; margin: 0;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()

# ─── Agent Pipeline Overview ──────────────────────────────────────────────────
st.subheader("🤖 Multi-Agent Pipeline")
st.caption("NeuroMate uses six specialised AI agents that collaborate to process your input end-to-end.")

pipeline = [
    ("🎯", "Intake", "Parses raw input"),
    ("📊", "Priority", "Ranks by importance"),
    ("🗓", "Scheduler", "Builds daily plan"),
    ("🧘", "Wellness", "Checks overload"),
    ("💡", "Recommend", "Suggests actions"),
    ("🪞", "Reflection", "Composes response"),
]

pipe_cols = st.columns(len(pipeline))
for i, (icon, name, desc) in enumerate(pipeline):
    with pipe_cols[i]:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 0.75rem 0.25rem;">
                <div style="font-size: 1.5rem;">{icon}</div>
                <p style="font-weight: 600; font-size: 0.85rem; margin: 0.25rem 0 0.1rem 0;">{name}</p>
                <p style="color: #64748b; font-size: 0.75rem; margin: 0;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if i < len(pipeline) - 1:
            pass  # Arrow rendered via column layout

st.divider()

# ─── CTA ─────────────────────────────────────────────────────────────────────
cta_col1, cta_col2, cta_col3 = st.columns([1, 1, 1])
with cta_col2:
    if st.button("🚀 Go to Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")
