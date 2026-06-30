"""
pages/Journal.py — NeuroMate Journal Page
==========================================
A secure, password-protected personal journal.

Security Design:
    - Entries are only accessible after the user enters the correct password.
    - The password is verified against a SHA-256 hash stored in .env.
    - If no password is configured, a friendly setup prompt is shown.
    - Journal entries are stored in a separate data file (data/journal.json).
    - Agents cannot access journal data without explicit UI authentication.
    - Future versions may add AES encryption for entries at rest.

Features:
    - Write daily journal entries with mood selection.
    - View past entries by date.
    - Entries are isolated from the rest of the application.
"""

import streamlit as st
from datetime import date, datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server as mcp
from config import APP_NAME, JOURNAL_PASSWORD_HASH, DATA_DIR
from utils import verify_password, init_session_key, hash_password

# ─── Session State ────────────────────────────────────────────────────────────
init_session_key("journal_authenticated", False)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1 class="page-title">📓 Private Journal</h1>
        <p class="page-subtitle">Your thoughts, safely kept. Password-protected and isolated.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


AUTH_FILE = os.path.join(DATA_DIR, "journal_auth.json")

def get_journal_password_hash():
    if JOURNAL_PASSWORD_HASH:
        return JOURNAL_PASSWORD_HASH
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r") as f:
                data = json.load(f)
                return data.get("password_hash")
        except Exception:
            return None
    return None

def set_journal_password(password):
    hashed = hash_password(password)
    with open(AUTH_FILE, "w") as f:
        json.dump({"password_hash": hashed}, f)
    return hashed

current_hash = get_journal_password_hash()

# ─── Configuration Check / Setup ───────────────────────────────────────────────
if not current_hash:
    st.markdown(
        """
        <div style="text-align:center; padding: 2rem 0 1rem 0;">
            <div style="font-size: 3rem;">🔐</div>
            <h3 style="margin-top: 0.5rem;">Secure Your Journal</h3>
            <p style="color: #9ca3af;">Create a password to keep your thoughts private and secure.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("journal_setup_form"):
        new_password = st.text_input(
            "Create a password",
            type="password",
            placeholder="Enter a strong password",
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Enter the password again",
        )
        submitted = st.form_submit_button("Create Password", use_container_width=True)

        if submitted:
            if not new_password:
                st.error("Password cannot be empty.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                set_journal_password(new_password)
                st.success("✅ Password set successfully! You can now access your journal.")
                st.rerun()
    st.stop()

# ─── Password Gate ────────────────────────────────────────────────────────────
if not st.session_state.journal_authenticated:
    st.markdown(
        """
        <div style="text-align:center; padding: 2rem 0 1rem 0;">
            <div style="font-size: 3rem;">🔐</div>
            <h3 style="margin-top: 0.5rem;">Journal Access</h3>
            <p style="color: #9ca3af;">Enter your journal password to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("journal_auth_form"):
        password_input = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your journal password",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("🔓 Unlock Journal", use_container_width=True)

        if submitted:
            if verify_password(password_input, current_hash):
                st.session_state.journal_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    st.caption(
        "🔒 Your journal password is hashed and never stored in plain text. "
        "NeuroMate agents cannot access your entries without your authentication."
    )
    st.stop()

# ─── Journal UI (Authenticated) ───────────────────────────────────────────────

# Lock button
lock_col, _ = st.columns([1, 5])
with lock_col:
    if st.button("🔒 Lock", help="Lock the journal and clear the session"):
        st.session_state.journal_authenticated = False
        st.rerun()

st.markdown("### ✍️ New Entry")

MOOD_OPTIONS = {
    "😄 Great": "great",
    "🙂 Good": "good",
    "😐 Neutral": "neutral",
    "😔 Low": "low",
    "😞 Rough": "rough",
}

with st.form("journal_entry_form", clear_on_submit=True):
    entry_date = st.date_input("Entry Date", value=date.today(), max_value=date.today(), format="MM/DD/YYYY")
    mood_label = st.radio(
        "How are you feeling today?",
        options=list(MOOD_OPTIONS.keys()),
        horizontal=True,
        index=2,
    )
    entry_content = st.text_area(
        "Your thoughts…",
        placeholder=(
            "What happened today? How did it make you feel? "
            "What are you grateful for? What would you do differently?"
        ),
        height=200,
    )
    submitted_entry = st.form_submit_button("💾 Save Entry", use_container_width=True)

    if submitted_entry:
        if not entry_content.strip():
            st.error("Your journal entry cannot be empty.")
        else:
            mood_value = MOOD_OPTIONS[mood_label]
            mcp.save_journal(
                date=entry_date.isoformat(),
                content=entry_content.strip(),
                mood=mood_value,
            )
            st.success("✅ Journal entry saved securely.")
            st.rerun()

# ─── Past Entries ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 📖 Past Entries")

all_entries = mcp.load_journal()
if all_entries:
    # Sort entries most recent first
    sorted_entries = sorted(all_entries, key=lambda e: e.date, reverse=True)
    mood_display = {
        "great": "😄 Great", "good": "🙂 Good", "neutral": "😐 Neutral",
        "low": "😔 Low", "rough": "😞 Rough",
    }
    for entry in sorted_entries:
        with st.expander(
            f"📅 {entry.date} &nbsp;·&nbsp; {mood_display.get(entry.mood, '😐 Neutral')}",
            expanded=False,
        ):
            st.markdown(entry.content)
            st.caption(f"Written on {entry.created_at[:10]}")
else:
    st.info(
        "No journal entries yet. Write your first entry above! 📝",
        icon="📓",
    )
