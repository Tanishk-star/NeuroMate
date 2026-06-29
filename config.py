"""
config.py — NeuroMate Central Configuration
============================================
All application settings are loaded from environment variables.
Never hardcode secrets or API keys in this file.

Security Note:
    - Secrets are loaded via python-dotenv from a .env file (excluded from Git).
    - The .env.example file documents required variables without real values.
    - In production (Streamlit Cloud), set variables in the Secrets dashboard.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


# ---------------------------------------------------------------------------
# Gemini API Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
"""
Google Gemini API key.
Required for all AI agent functionality.
Set this in your .env file or Streamlit Cloud Secrets.
"""

GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
"""
The Gemini model to use across all agents.
Options: gemini-2.0-flash, gemini-1.5-pro, gemini-2.5-pro
"""


# ---------------------------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------------------------

APP_NAME: str = "NeuroMate"
APP_VERSION: str = "0.1.0"
APP_DESCRIPTION: str = "Your AI Daily Decision Companion"

DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
"""
Enable verbose logging and debug output.
Set DEBUG_MODE=true in .env during development.
"""

# ---------------------------------------------------------------------------
# Journal Security
# ---------------------------------------------------------------------------

JOURNAL_PASSWORD_HASH: str = os.getenv("JOURNAL_PASSWORD_HASH", "")
"""
SHA-256 hash of the journal access password.
Never store plain-text passwords — only the hash goes here.
Generate with: python -c "import hashlib; print(hashlib.sha256(b'yourpassword').hexdigest())"
"""

# ---------------------------------------------------------------------------
# Storage Configuration
# ---------------------------------------------------------------------------

DATA_DIR: str = os.getenv("DATA_DIR", "data")
"""
Directory where local data files (JSON/SQLite) are stored.
Will be created automatically if it does not exist.
"""

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/neuromate.db")
"""
Database connection URL.
Defaults to a local SQLite file. Replace with a PostgreSQL URL for production.
Example: postgresql://user:password@host:5432/neuromate
"""


# ---------------------------------------------------------------------------
# Future Deployment Settings
# ---------------------------------------------------------------------------

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
"""
Deployment environment identifier.
Values: 'development', 'staging', 'production'
Used to toggle certain behaviours (e.g., stricter error handling in production).
"""

ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "").split(",")
"""
Comma-separated list of allowed CORS origins (for future API layer).
"""


# ---------------------------------------------------------------------------
# Validation Helper
# ---------------------------------------------------------------------------

def validate_config() -> list[str]:
    """
    Validate that all required configuration values are present.

    Returns:
        list[str]: A list of missing configuration variable names.
                   An empty list means configuration is complete.

    Usage:
        missing = validate_config()
        if missing:
            st.error(f"Missing config: {missing}")
    """
    required = {"GEMINI_API_KEY": GEMINI_API_KEY}
    return [key for key, value in required.items() if not value]
