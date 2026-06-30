"""
pages/Settings.py — NeuroMate Settings Page
=============================================
User preferences management.

Allows the user to configure:
    - Display name
    - AI buddy personality
    - Language preference
    - Work hours
    - Break intervals
    - Notification preferences
    - Theme (stored in preferences; Streamlit theme set via config.toml)

All preferences are saved via the MCP tool layer to preserve
the clean separation between UI and data storage.
"""

import streamlit as st

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server as mcp
from utils import init_session_key
from config import APP_NAME, APP_VERSION, validate_config

# ─── Load current preferences ─────────────────────────────────────────────────
prefs = mcp.load_preferences()
init_session_key("user_name", "Friend")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1 class="page-title">⚙️ Settings</h1>
        <p class="page-subtitle">Configure your NeuroMate environment and personal preferences. · v{APP_VERSION}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Configuration Validation & Warning ────────────────────────────────────────
missing_config = validate_config()

# ─── API Key Configuration ───────────────────────────────────────────
st.subheader("🔑 API Configuration")
if missing_config:
    st.warning(
        f"⚙️ **System Configuration Required**\n\n"
        f"The system is missing: `{', '.join(missing_config)}`.\n\n"
        f"To enable Gemini AI agents, please enter your Gemini API key below.",
        icon="🔑",
    )

with st.form("settings_api_form"):
    from config import GEMINI_API_KEY
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=GEMINI_API_KEY,
        type="password",
        placeholder="AIzaSy...",
        help="Your key is stored locally in your .env file."
    )
    if st.form_submit_button("Save API Key", use_container_width=True):
        if api_key_input.strip():
            # Write to .env
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_lines = f.readlines()
            
            new_lines = []
            key_found = False
            for line in env_lines:
                if line.startswith("GEMINI_API_KEY="):
                    new_lines.append(f"GEMINI_API_KEY={api_key_input.strip()}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"GEMINI_API_KEY={api_key_input.strip()}\n")
                
            with open(env_path, "w") as f:
                f.writelines(new_lines)
                
            st.success("✅ API Key saved! Please restart the application for changes to take effect.")
        else:
            st.error("API Key cannot be empty.")
            
st.divider()

# ─── Profile Section ──────────────────────────────────────────────────────────
st.subheader("👤 Profile")
with st.form("settings_profile_form"):
    user_name = st.text_input(
        "Your Name",
        value=st.session_state.user_name,
        placeholder="How should NeuroMate address you?",
        max_chars=50,
    )

    language = st.selectbox(
        "Language",
        options=["en", "es", "fr", "de", "pt", "zh", "hi", "ar"],
        index=["en", "es", "fr", "de", "pt", "zh", "hi", "ar"].index(prefs.language),
        format_func=lambda x: {
            "en": "🇬🇧 English", "es": "🇪🇸 Spanish", "fr": "🇫🇷 French",
            "de": "🇩🇪 German", "pt": "🇧🇷 Portuguese", "zh": "🇨🇳 Chinese",
            "hi": "🇮🇳 Hindi", "ar": "🇸🇦 Arabic",
        }.get(x, x),
    )

    if st.form_submit_button("Save Profile", use_container_width=True):
        st.session_state.user_name = user_name.strip() or "Friend"
        prefs.language = language
        mcp.save_preferences(prefs)
        st.success("✅ Profile saved!")

st.divider()

# ─── AI Companion Section ─────────────────────────────────────────────────────
st.subheader("🤖 AI Buddy Personality")
st.caption("Choose how your NeuroMate companion communicates with you.")

with st.form("settings_personality_form"):
    personality_options = {
        "friendly": "😊 Friendly — warm, encouraging, and conversational",
        "professional": "💼 Professional — concise, structured, and focused",
        "motivational": "🔥 Motivational — energetic, bold, and action-oriented",
        "zen": "🧘 Zen — calm, mindful, and reflective",
    }
    personality = st.radio(
        "Select Personality",
        options=list(personality_options.keys()),
        format_func=lambda x: personality_options[x],
        index=list(personality_options.keys()).index(prefs.buddy_personality),
        label_visibility="collapsed",
    )

    if st.form_submit_button("Save Personality", use_container_width=True):
        prefs.buddy_personality = personality
        mcp.save_preferences(prefs)
        st.success(f"✅ Personality set to **{personality_options[personality]}**")

st.divider()

# ─── Work Schedule Section ────────────────────────────────────────────────────
st.subheader("⏰ Work Schedule")
st.caption("Define your working hours so the Scheduler Agent can plan effectively.")

with st.form("settings_schedule_form"):
    sched_col1, sched_col2 = st.columns(2)
    with sched_col1:
        work_start = st.number_input(
            "Work Start Hour (24h)",
            min_value=0,
            max_value=23,
            value=prefs.work_start_hour,
            step=1,
            help="e.g. 9 = 9:00 AM",
        )
    with sched_col2:
        work_end = st.number_input(
            "Work End Hour (24h)",
            min_value=0,
            max_value=23,
            value=prefs.work_end_hour,
            step=1,
            help="e.g. 18 = 6:00 PM",
        )
    break_interval = st.slider(
        "Break Interval (minutes)",
        min_value=30,
        max_value=180,
        value=prefs.break_interval_minutes,
        step=15,
        help="How often the Wellness Agent should recommend a break.",
    )

    if st.form_submit_button("Save Schedule", use_container_width=True):
        if work_start >= work_end:
            st.error("Work start hour must be earlier than work end hour.")
        else:
            prefs.work_start_hour = int(work_start)
            prefs.work_end_hour = int(work_end)
            prefs.break_interval_minutes = break_interval
            mcp.save_preferences(prefs)
            st.success("✅ Work schedule saved!")

st.divider()

# ─── Notifications Section ────────────────────────────────────────────────────
st.subheader("🔔 Notifications")
with st.form("settings_notifications_form"):
    notifications_enabled = st.toggle(
        "Enable Notifications",
        value=prefs.notifications_enabled,
        help="Reminders and nudges from your AI agents (future feature).",
    )

    if st.form_submit_button("Save Notifications", use_container_width=True):
        prefs.notifications_enabled = notifications_enabled
        mcp.save_preferences(prefs)
        status = "enabled" if notifications_enabled else "disabled"
        st.success(f"✅ Notifications {status}.")

st.divider()

# ─── About Section ────────────────────────────────────────────────────────────
st.subheader("ℹ️ About NeuroMate")
with st.container(border=True):
    st.markdown(
        f"""
        **{APP_NAME}** — Your AI Daily Decision Companion

        | | |
        |---|---|
        | **Version** | {APP_VERSION} |
        | **Built with** | Python · Streamlit · Google Gemini |
        | **Architecture** | Multi-Agent AI System |
        | **Competition** | Kaggle AI Agents Capstone |

        _Designed to reduce decision fatigue and help you focus on what matters._
        """
    )
