"""
database.py — NeuroMate Data Models & Storage Layer
=====================================================
Defines the core data models for NeuroMate.

Design Principle:
    This module uses simple Python dataclasses as models.
    The storage layer is currently in-memory / JSON-file based.
    It is designed to be replaced with SQLite (via SQLAlchemy or
    another ORM) with minimal changes to the rest of the codebase.

    Agents and pages should NEVER access data directly.
    All data access goes through mcp_server.py (the tool layer).

Future Upgrade Path:
    1. Replace dataclasses with SQLAlchemy ORM models.
    2. Update DatabaseManager to use a real DB session.
    3. No changes required in agents or pages.
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from config import DATA_DIR
from utils import ensure_dir, get_logger

logger = get_logger(__name__)

# Ensure data directory exists
ensure_dir(DATA_DIR)

# File paths for local JSON storage (temporary until DB is wired up)
_TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
_EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
_JOURNAL_FILE = os.path.join(DATA_DIR, "journal.json")
_PREFERENCES_FILE = os.path.join(DATA_DIR, "preferences.json")
_USERS_FILE = os.path.join(DATA_DIR, "users.json")


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class User:
    """
    Represents a NeuroMate user profile.

    Fields:
        id (str): Unique user identifier (UUID).
        name (str): Display name.
        email (str): User's email address.
        created_at (str): ISO 8601 timestamp of account creation.
        is_active (bool): Whether the account is active.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "NeuroMate User"
    email: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class Task:
    """
    Represents a single user task.

    Fields:
        id (str): Unique task identifier (UUID).
        title (str): Short task title.
        description (str): Detailed task description.
        priority (str): 'high', 'medium', or 'low'.
        status (str): 'pending', 'in_progress', or 'completed'.
        due_date (Optional[str]): ISO 8601 date string.
        tags (list[str]): Categorisation tags (e.g., ['work', 'health']).
        created_at (str): ISO 8601 creation timestamp.
        updated_at (str): ISO 8601 last-updated timestamp.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: str = "medium"          # 'high' | 'medium' | 'low'
    status: str = "pending"           # 'pending' | 'in_progress' | 'completed'
    due_date: Optional[str] = None    # ISO 8601 date string
    tags: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Event:
    """
    Represents a calendar event or scheduled appointment.

    Fields:
        id (str): Unique event identifier (UUID).
        title (str): Event name.
        description (str): Details about the event.
        start_time (str): ISO 8601 start datetime.
        end_time (str): ISO 8601 end datetime.
        location (str): Physical or virtual location.
        event_type (str): 'meeting', 'personal', 'health', 'other'.
        created_at (str): ISO 8601 creation timestamp.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    start_time: str = ""
    end_time: str = ""
    location: str = ""
    event_type: str = "personal"      # 'meeting' | 'personal' | 'health' | 'other'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class JournalEntry:
    """
    Represents a single secure journal entry.

    Security Note:
        Journal entries are stored separately from other data and are
        only accessible via a password-protected interface.
        Future versions may encrypt entries at rest.

    Fields:
        id (str): Unique entry identifier (UUID).
        date (str): ISO 8601 date string for the entry.
        content (str): The journal text body.
        mood (str): User's mood tag for the entry.
        created_at (str): ISO 8601 creation timestamp.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: str = field(default_factory=lambda: datetime.now().date().isoformat())
    content: str = ""
    mood: str = "neutral"             # 'great' | 'good' | 'neutral' | 'low' | 'rough'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UserPreferences:
    """
    Stores user-configurable application preferences.

    Fields:
        user_id (str): Associated user ID.
        language (str): Preferred language code (e.g., 'en', 'es').
        theme (str): UI theme — 'dark' or 'light'.
        buddy_personality (str): AI companion personality style.
        notifications_enabled (bool): Whether reminders are active.
        work_start_hour (int): Start of user's workday (24-hour clock).
        work_end_hour (int): End of user's workday (24-hour clock).
        break_interval_minutes (int): How often to suggest breaks.
    """
    user_id: str = "default"
    language: str = "en"
    theme: str = "dark"
    buddy_personality: str = "friendly"   # 'friendly' | 'professional' | 'motivational' | 'zen'
    notifications_enabled: bool = True
    work_start_hour: int = 9
    work_end_hour: int = 18
    break_interval_minutes: int = 90


# ---------------------------------------------------------------------------
# Database Manager
# ---------------------------------------------------------------------------

class DatabaseManager:
    """
    Simple JSON-based persistence layer.

    All read/write operations go through this class.
    Replace the internal implementation with SQLAlchemy or another
    ORM without changing the public interface.

    Usage:
        db = DatabaseManager()
        tasks = db.read_all(Task, _TASKS_FILE)
        db.write_all(tasks, _TASKS_FILE)
    """

    @staticmethod
    def read_all(model_class: type, filepath: str) -> list:
        """
        Load all records from a JSON file and deserialize them.

        Args:
            model_class: The dataclass type to reconstruct.
            filepath (str): Path to the JSON data file.

        Returns:
            list: List of deserialized model instances.
        """
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [model_class(**item) for item in raw]
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return []

    @staticmethod
    def write_all(records: list, filepath: str) -> None:
        """
        Serialize and save all records to a JSON file.

        Args:
            records (list): List of dataclass instances to save.
            filepath (str): Path to the JSON data file.
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([asdict(r) for r in records], f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to write {filepath}: {e}")

    @staticmethod
    def find_by_id(records: list, record_id: str):
        """
        Find a single record by its 'id' field.

        Args:
            records (list): List of dataclass instances.
            record_id (str): The UUID to search for.

        Returns:
            dataclass instance or None.
        """
        return next((r for r in records if r.id == record_id), None)


# Module-level singleton for convenience
db = DatabaseManager()
