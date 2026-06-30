"""
app.py — NeuroMate Main Application Entry Point
=================================================
Run with: streamlit run app.py

Architecture:
    Uses st.navigation() + st.Page() (Streamlit 1.36+ multipage API).
    st.set_page_config() is called exactly ONCE here.
    CSS is injected globally via apply_css_only().
    Each page file handles its own content only.
"""

import streamlit as st
import sys
import os

# Ensure project root is on the Python path for clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from utils import today_label, init_session_key, apply_css_only

# ─── Page Config (called exactly ONCE for the entire app) ────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS (injected once, applies to every page) ───────────────────────
apply_css_only()

# ─── Global Session State ────────────────────────────────────────────────────
init_session_key("user_name", "Friend")
init_session_key("chat_history", [])
init_session_key("journal_authenticated", False)
init_session_key("pipeline_results", {})

# ─── Page Registry (st.navigation API) ───────────────────────────────────────
# Each st.Page() defines a page: the file path is relative to this file (app.py).
# All pages listed here are automatically registered for st.switch_page() use.

_home      = st.Page("pages/Home.py",      title="Home",          icon="🏠", default=True)
_dashboard = st.Page("pages/Dashboard.py", title="Dashboard",     icon="📊")
_planner   = st.Page("pages/Planner.py",   title="Daily Planner", icon="🗓")
_companion = st.Page("pages/Companion.py", title="AI Companion",  icon="💬")
_insights  = st.Page("pages/Insights.py",  title="Insights",      icon="📈")
_journal   = st.Page("pages/Journal.py",   title="Journal",       icon="📓")
_settings  = st.Page("pages/Settings.py",  title="Settings",      icon="⚙️")

pg = st.navigation(
    {
        "NeuroMate": [_home, _dashboard],
        "Productivity": [_planner, _insights],
        "AI & Personal": [_companion, _journal],
        "System": [_settings],
    }
)

# ─── Sidebar (runs on every page navigation) ─────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
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

# ─── Run the selected page ────────────────────────────────────────────────────
pg.run()
