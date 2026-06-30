"""
pages/Home.py — NeuroMate Welcome / Landing Page
==================================================
The default landing page displayed when the app first loads.
Contains the welcome hero, feature overview, and agent pipeline diagram.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import APP_NAME, APP_DESCRIPTION

# ─── Hero Section ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align: center; padding: 3rem 2rem 2rem 2rem;">
        <div style="font-size: 5rem; margin-bottom: 1rem;">🧠</div>
        <h1 style="font-size: 2.75rem; font-weight: 800; margin: 0;
                   background: linear-gradient(90deg, #ffffff, #9ca3af);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Welcome to {APP_NAME}
        </h1>
        <p style="font-size: 1.2rem; color: #64748b; margin-top: 0.75rem;
                  max-width: 600px; margin-left: auto; margin-right: auto;">
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

# ─── Feature Cards ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="medium")

features = [
    ("📋", "Smart Task Management",       "Add and organise tasks. AI agents prioritise them by urgency and importance."),
    ("🗓", "Intelligent Scheduling",       "Time-block your day automatically based on your priorities and energy levels."),
    ("🧘", "Wellness Monitoring",          "Get nudged to take breaks, hydrate, and avoid burnout before it happens."),
    ("💡", "Personalised Recommendations","Context-aware suggestions tailored to your goals and personality."),
    ("📓", "Private Journal",             "A secure, password-protected diary to capture your thoughts and track mood trends."),
    ("📊", "Productivity Insights",       "Understand your patterns and improve week over week with AI analytics."),
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

# ─── Agent Pipeline Diagram ───────────────────────────────────────────────────
st.subheader("🤖 Multi-Agent Pipeline")
st.caption("NeuroMate uses six specialised AI agents that collaborate to process your input end-to-end.")

pipeline = [
    ("🎯", "Intake",      "Parses raw input"),
    ("📊", "Priority",    "Ranks by importance"),
    ("🗓", "Scheduler",   "Builds daily plan"),
    ("🧘", "Wellness",    "Checks overload"),
    ("💡", "Recommend",   "Suggests actions"),
    ("🪞", "Reflection",  "Composes response"),
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

st.divider()

# ─── CTA Button ───────────────────────────────────────────────────────────────
_, cta_col, _ = st.columns([1, 1, 1])
with cta_col:
    if st.button("🚀 Go to Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")
