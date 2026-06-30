"""
pages/Companion.py — NeuroMate AI Companion Page
==================================================
The conversational AI interface.

This page will host the full multi-agent pipeline conversation in Phase 2.
Currently provides a polished placeholder chat UI.

Planned features:
    - Free-form conversation with the AI pipeline.
    - Automatic task extraction from chat.
    - Real-time agent status indicators.
    - Conversation history with session persistence.
"""

import streamlit as st

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import init_session_key

# ─── Session State ────────────────────────────────────────────────────────────
init_session_key("chat_history", [
    {
        "role": "assistant",
        "content": (
            "👋 Hi! I'm **NeuroMate**, your AI decision companion.\n\n"
            "Tell me about your day, your tasks, or anything that's on your mind — "
            "and I'll help you cut through the noise and focus on what matters."
        ),
    }
])

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <h1 class="page-title">💬 AI Companion</h1>
        <p class="page-subtitle">Your personal multi-agent AI assistant — powered by Google Gemini.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Agent Pipeline Status ────────────────────────────────────────────────────
with st.expander("🔧 Agent Pipeline Status", expanded=False):
    agents = [
        ("🎯 Intake Agent", "Ready", "Parses your input into structured tasks"),
        ("📊 Priority Agent", "Ready", "Ranks tasks by urgency and importance"),
        ("🗓 Scheduler Agent", "Ready", "Builds your time-blocked daily plan"),
        ("🧘 Wellness Agent", "Ready", "Monitors your schedule for overload"),
        ("💡 Recommendation Agent", "Ready", "Generates personalised suggestions"),
        ("🪞 Reflection Agent", "Ready", "Composes your final AI briefing"),
    ]
    cols = st.columns(3)
    for i, (name, status, desc) in enumerate(agents):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(desc)
                st.markdown(
                    f"<span style='color:#10b981; font-size:0.8rem;'>● {status}</span>",
                    unsafe_allow_html=True,
                )

st.divider()

# ─── Chat Interface ───────────────────────────────────────────────────────────
# Render conversation history
chat_container = st.container(height=420)
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="🧠" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# ─── Chat Input ───────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Tell me about your tasks, goals, or how you're feeling today…",
    disabled=False,
)

def get_fallback_response(user_text: str) -> str:
    text = user_text.lower()
    if any(word in text for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm ready to help you organize your day. What's on your mind?"
    elif any(word in text for word in ["schedule", "plan", "time"]):
        return "I can help with scheduling. Try adding some tasks in the app, and I'll generate a time-blocked plan for you!"
    elif any(word in text for word in ["productivity", "focus", "work", "study"]):
        return "To improve productivity, I recommend the Pomodoro technique. Work for 25 minutes, then take a 5-minute break. Ready to start?"
    elif any(word in text for word in ["tired", "stress", "wellness", "break", "overwhelmed"]):
        return "It sounds like you might be pushing yourself hard. Remember to take a break, hydrate, and stretch. Your well-being comes first."
    elif any(word in text for word in ["meal", "food", "eat", "hungry"]):
        return "Don't forget to fuel up! A balanced meal will help keep your energy levels steady throughout the day."
    elif any(word in text for word in ["motivat", "stuck", "procrastinat"]):
        return "You've got this! Start with the smallest, easiest task to build momentum. Taking that first step is often the hardest part."
    else:
        return (
            "I'm currently operating in offline mode, but I'm here for you! "
            "Tell me if you need help with scheduling, productivity, wellness, or motivation."
        )

if user_input:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display user message immediately
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

    # Check for Gemini API key
    from config import GEMINI_API_KEY
    api_key_configured = bool(GEMINI_API_KEY)
    
    if api_key_configured:
        from agents import IntakeAgent, PriorityAgent, SchedulerAgent, WellnessAgent, RecommendationAgent, ReflectionAgent
        intake = IntakeAgent()
        priority = PriorityAgent()
        scheduler = SchedulerAgent()
        wellness = WellnessAgent()
        recommendation = RecommendationAgent()
        reflection = ReflectionAgent()

        structured = intake.process(user_input)
        ranked = priority.process(structured)
        scheduled = scheduler.process(ranked)
        well = wellness.process(scheduled)
        rec = recommendation.process(well)
        final = reflection.process(rec)

        response_text = final.get("final_message", "I'm sorry, I couldn't process that.")
    else:
        response_text = get_fallback_response(user_input)

    # Add assistant response to history
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
    
    # Rerun to update chat history
    st.rerun()

# ─── Clear Chat ───────────────────────────────────────────────────────────────
if len(st.session_state.chat_history) > 1:
    if st.button("🗑 Clear conversation", use_container_width=False):
        st.session_state.chat_history = [st.session_state.chat_history[0]]
        st.rerun()
