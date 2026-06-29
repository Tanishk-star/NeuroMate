"""
utils.py — NeuroMate Shared Utilities
======================================
A collection of helper functions used across the application.

Design Principle:
    Keep utilities small, pure (no side effects where possible),
    and independently testable. Avoid importing from other NeuroMate
    modules here to prevent circular dependencies.
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any

import streamlit as st


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Create and return a named logger with consistent formatting.

    Args:
        name (str): Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("Agent started.")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s — %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


# ---------------------------------------------------------------------------
# Security Utilities
# ---------------------------------------------------------------------------

def hash_password(plain_text: str) -> str:
    """
    Hash a plain-text password using SHA-256.

    Security Note:
        SHA-256 is used here for simplicity. For production systems handling
        real user authentication, use bcrypt or argon2 instead.

    Args:
        plain_text (str): The raw password string.

    Returns:
        str: Hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(plain_text.encode()).hexdigest()


def verify_password(plain_text: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored hash.

    Args:
        plain_text (str): The password to verify.
        hashed (str): The stored SHA-256 hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return hash_password(plain_text) == hashed


# ---------------------------------------------------------------------------
# Date & Time Utilities
# ---------------------------------------------------------------------------

def get_current_datetime() -> datetime:
    """Return the current local datetime."""
    return datetime.now()


def format_datetime(dt: datetime, fmt: str = "%m/%d/%Y %I:%M %p") -> str:
    """
    Format a datetime object into a human-readable string.

    Args:
        dt (datetime): The datetime to format.
        fmt (str): strftime format string.

    Returns:
        str: Formatted date string.
    """
    return dt.strftime(fmt)


def today_label() -> str:
    """Return today's date as a readable label, e.g. 'Saturday, June 28 2025'."""
    return format_datetime(get_current_datetime(), "%m/%d/%Y")


# ---------------------------------------------------------------------------
# Streamlit Session State Utilities
# ---------------------------------------------------------------------------

def init_session_key(key: str, default: Any) -> None:
    """
    Safely initialize a Streamlit session state key if it does not exist.

    Args:
        key (str): The session state key name.
        default (Any): The default value to assign if the key is missing.

    Example:
        init_session_key("tasks", [])
    """
    if key not in st.session_state:
        st.session_state[key] = default


def clear_session_keys(*keys: str) -> None:
    """
    Remove specific keys from Streamlit session state.

    Args:
        *keys (str): One or more session state key names to remove.
    """
    for key in keys:
        st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# Data Utilities
# ---------------------------------------------------------------------------

def ensure_dir(path: str) -> str:
    """
    Create a directory (and all parents) if it does not already exist.

    Args:
        path (str): Directory path to create.

    Returns:
        str: The same path, for easy chaining.
    """
    os.makedirs(path, exist_ok=True)
    return path


def truncate_text(text: str, max_chars: int = 100, suffix: str = "…") -> str:
    """
    Truncate a string to a maximum character length.

    Args:
        text (str): The source string.
        max_chars (int): Maximum number of characters before truncation.
        suffix (str): String appended when truncation occurs.

    Returns:
        str: Truncated string.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + suffix


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely retrieve a nested value from a dictionary without raising KeyError.

    Args:
        data (dict): The source dictionary.
        *keys (str): Ordered sequence of keys to traverse.
        default (Any): Value returned if any key is missing.

    Returns:
        Any: The nested value, or default.

    Example:
        value = safe_get(config, "database", "host", default="localhost")
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


# ---------------------------------------------------------------------------
# Theme Customization
# ---------------------------------------------------------------------------

def apply_custom_theme(page_title: str, page_icon: str) -> None:
    """
    Applies the custom NeuroMate design system (Notion/Linear/Apple style)
    and configures page-specific settings.
    This must be called at the very beginning of each page.
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.markdown(
        """
        <style>
        /* --- Import Inter Font --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* --- Global Reset & Scrollbars --- */
        html, body, [class*="st-"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #0b0f19;
            color: #f3f4f6;
        }
        
        /* Set base app background to Slate Dark */
        .stApp {
            background: radial-gradient(circle at top right, #111a2e 0%, #0b0f19 100%);
        }
        
        /* --- Custom Scrollbar --- */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0b0f19;
        }
        ::-webkit-scrollbar-thumb {
            background: #1f2937;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #374151;
        }

        /* --- Hide default Streamlit headers and footers --- */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        [data-testid="stHeader"] {background: transparent;}
        
        /* --- Sidebar Styling (Linear/Notion inspired) --- */
        [data-testid="stSidebar"] {
            background-color: #0d1220 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        [data-testid="stSidebarNav"] {
            padding-top: 1.5rem;
        }
        [data-testid="stSidebarNav"] a {
            font-weight: 500;
            font-size: 0.9rem;
            color: #9ca3af !important;
            border-radius: 8px;
            padding: 8px 12px;
            margin: 4px 12px;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(99, 102, 241, 0.08) !important;
            color: #e5e7eb !important;
        }
        [data-testid="stSidebarNav"] .active {
            background-color: rgba(99, 102, 241, 0.15) !important;
            color: #a5b4fc !important;
            font-weight: 600;
        }
        
        /* --- Dashboard Custom Metric Card (Linear Grid) --- */
        .stat-card-container {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: rgba(17, 24, 39, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            transition: all 0.25s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .stat-card-title {
            color: #9ca3af;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .stat-card-value {
            color: #f3f4f6;
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        /* --- Schedule Timeline --- */
        .timeline {
            border-left: 2px solid rgba(99, 102, 241, 0.2);
            margin-left: 12px;
            padding-left: 24px;
            position: relative;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 24px;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -33px;
            top: 4px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #111827;
            border: 3px solid #6366f1;
            transition: all 0.2s ease;
        }
        .timeline-item:hover::before {
            background: #6366f1;
            box-shadow: 0 0 8px #6366f1;
        }
        .timeline-time {
            font-size: 0.85rem;
            font-weight: 600;
            color: #818cf8;
            margin-bottom: 2px;
        }
        .timeline-content {
            background: rgba(17, 24, 39, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 8px;
            padding: 12px 16px;
        }
        
        /* --- Glowing AI Recommendation Card --- */
        .rec-card {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.08);
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }
        .rec-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            transform: translateX(-100%);
            transition: 0.6s;
        }
        .rec-card:hover::after {
            transform: translateX(100%);
        }
        
        /* --- Linear Style Task Card --- */
        .task-list-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .task-card-new {
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
        }
        .task-card-new:hover {
            border-color: rgba(255, 255, 255, 0.1);
            background: rgba(17, 24, 39, 0.8);
        }
        .task-badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }
        .badge-high {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .badge-medium {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-low {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        /* --- Sidebar Profile Area --- */
        .sidebar-profile {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin: 16px 12px;
        }
        .profile-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: white;
            font-size: 0.9rem;
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
        }
        .profile-info {
            display: flex;
            flex-direction: column;
        }
        .profile-name {
            font-weight: 600;
            font-size: 0.85rem;
            color: #e5e7eb;
        }
        .profile-status {
            font-size: 0.7rem;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .profile-status-dot {
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px #10b981;
        }
        
        /* --- Form Input styling --- */
        div[data-baseweb="input"] {
            background-color: rgba(17, 24, 39, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="textarea"] {
            background-color: rgba(17, 24, 39, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 8px !important;
        }
        button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #f3f4f6 !important;
        }
        button[kind="secondary"]:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
        }
        
        /* --- Header enhancements --- */
        .page-header {
            margin-bottom: 2rem;
        }
        .page-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin: 0;
            background: linear-gradient(to right, #ffffff, #9ca3af);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .page-subtitle {
            color: #9ca3af;
            font-size: 1rem;
            margin-top: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

