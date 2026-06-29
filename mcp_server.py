"""
mcp_server.py — NeuroMate MCP Tool Layer
==========================================
Centralized tool registry for all agent-to-data interactions.

Design Principle (MCP Pattern):
    AI Agents should NEVER directly read or write data.
    Instead, every agent calls a named "tool" from this module.
    This creates a clean separation between:
        - AI reasoning (agents/)
        - Data access (database.py)
        - Business logic (this file)

    This mirrors the Model Context Protocol (MCP) concept:
    a standardized tool layer that agents can discover and call.

    To upgrade storage (e.g., SQLite → PostgreSQL), only this file
    and database.py need changes. Agents remain untouched.

Tool Registry:
    Task Tools      → used by: IntakeAgent, PriorityAgent, SchedulerAgent
    Event Tools     → used by: SchedulerAgent
    Journal Tools   → used by: ReflectionAgent (password-gated in UI)
    Preference Tools→ used by: WellnessAgent, RecommendationAgent
"""

from datetime import datetime
from typing import Optional

from database import (
    DatabaseManager,
    Task,
    Event,
    JournalEntry,
    UserPreferences,
    _TASKS_FILE,
    _EVENTS_FILE,
    _JOURNAL_FILE,
    _PREFERENCES_FILE,
)
from utils import get_logger

logger = get_logger(__name__)
db = DatabaseManager()


# ===========================================================================
# Task Tools
# Used by: IntakeAgent, PriorityAgent, SchedulerAgent
# ===========================================================================

def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
    tags: Optional[list] = None,
) -> Task:
    """
    Create and persist a new task.

    Args:
        title (str): Short task title (required).
        description (str): Detailed description.
        priority (str): 'high', 'medium', or 'low'.
        due_date (Optional[str]): ISO 8601 date string.
        tags (Optional[list]): List of category tags.

    Returns:
        Task: The newly created Task object.

    Used by: IntakeAgent (creates tasks from user input)
    """
    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        tags=tags or [],
    )
    tasks = db.read_all(Task, _TASKS_FILE)
    tasks.append(task)
    db.write_all(tasks, _TASKS_FILE)
    logger.info(f"[add_task] Created task '{title}' (id={task.id})")
    return task


def get_tasks(status: Optional[str] = None) -> list[Task]:
    """
    Retrieve all tasks, optionally filtered by status.

    Args:
        status (Optional[str]): Filter by 'pending', 'in_progress', or 'completed'.
                                Pass None to return all tasks.

    Returns:
        list[Task]: Matching task records.

    Used by: PriorityAgent (reads tasks for ranking),
             SchedulerAgent (reads tasks for scheduling),
             Dashboard page (displays today's overview)
    """
    tasks = db.read_all(Task, _TASKS_FILE)
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


def update_task(task_id: str, **updates) -> Optional[Task]:
    """
    Update fields on an existing task.

    Args:
        task_id (str): UUID of the task to update.
        **updates: Keyword arguments matching Task field names.

    Returns:
        Optional[Task]: The updated Task, or None if not found.

    Used by: PriorityAgent (updates priority),
             SchedulerAgent (updates status),
             Planner page (user edits)
    """
    tasks = db.read_all(Task, _TASKS_FILE)
    task = db.find_by_id(tasks, task_id)
    if not task:
        logger.warning(f"[update_task] Task {task_id} not found.")
        return None
    for key, value in updates.items():
        if hasattr(task, key):
            setattr(task, key, value)
    task.updated_at = datetime.now().isoformat()
    db.write_all(tasks, _TASKS_FILE)
    logger.info(f"[update_task] Updated task {task_id}: {updates}")
    return task


def delete_task(task_id: str) -> bool:
    """
    Permanently remove a task by ID.

    Args:
        task_id (str): UUID of the task to delete.

    Returns:
        bool: True if deleted, False if not found.

    Used by: Planner page (user deletion)
    """
    tasks = db.read_all(Task, _TASKS_FILE)
    original_count = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) == original_count:
        logger.warning(f"[delete_task] Task {task_id} not found.")
        return False
    db.write_all(tasks, _TASKS_FILE)
    logger.info(f"[delete_task] Deleted task {task_id}")
    return True


# ===========================================================================
# Event Tools
# Used by: SchedulerAgent
# ===========================================================================

def add_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    event_type: str = "personal",
) -> Event:
    """
    Create and persist a new calendar event.

    Args:
        title (str): Event name (required).
        start_time (str): ISO 8601 start datetime (required).
        end_time (str): ISO 8601 end datetime (required).
        description (str): Event details.
        location (str): Physical or virtual location.
        event_type (str): 'meeting', 'personal', 'health', or 'other'.

    Returns:
        Event: The newly created Event object.

    Used by: SchedulerAgent (adds AI-generated schedule blocks),
             Planner page (user adds events manually)
    """
    event = Event(
        title=title,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
        event_type=event_type,
    )
    events = db.read_all(Event, _EVENTS_FILE)
    events.append(event)
    db.write_all(events, _EVENTS_FILE)
    logger.info(f"[add_event] Created event '{title}' (id={event.id})")
    return event


def get_events(date: Optional[str] = None) -> list[Event]:
    """
    Retrieve all events, optionally filtered by date.

    Args:
        date (Optional[str]): ISO 8601 date string (YYYY-MM-DD) to filter by.
                              Pass None to return all events.

    Returns:
        list[Event]: Matching event records.

    Used by: SchedulerAgent (checks calendar for conflicts),
             Dashboard page (shows today's events)
    """
    events = db.read_all(Event, _EVENTS_FILE)
    if date:
        events = [e for e in events if e.start_time.startswith(date)]
    return events


# ===========================================================================
# Journal Tools
# Used by: ReflectionAgent (UI enforces password gate before calling these)
# ===========================================================================

def save_journal(date: str, content: str, mood: str = "neutral") -> JournalEntry:
    """
    Save a new journal entry.

    Security Note:
        This function must only be called AFTER the user has
        successfully authenticated via the Journal page password gate.
        Never expose journal content to other agents or pages.

    Args:
        date (str): ISO 8601 date string for the entry.
        content (str): The journal text body.
        mood (str): Mood tag for the entry.

    Returns:
        JournalEntry: The saved journal entry.

    Used by: ReflectionAgent (persists daily reflection),
             Journal page (user writes entries)
    """
    entry = JournalEntry(date=date, content=content, mood=mood)
    entries = db.read_all(JournalEntry, _JOURNAL_FILE)
    entries.append(entry)
    db.write_all(entries, _JOURNAL_FILE)
    logger.info(f"[save_journal] Saved journal entry for {date}")
    return entry


def load_journal(date: Optional[str] = None) -> list[JournalEntry]:
    """
    Load journal entries, optionally filtered by date.

    Security Note:
        Only accessible through the password-protected Journal page.

    Args:
        date (Optional[str]): ISO 8601 date string to filter by.

    Returns:
        list[JournalEntry]: Matching journal entries.

    Used by: ReflectionAgent, Journal page
    """
    entries = db.read_all(JournalEntry, _JOURNAL_FILE)
    if date:
        entries = [e for e in entries if e.date == date]
    return entries


# ===========================================================================
# Preference Tools
# Used by: WellnessAgent, RecommendationAgent, Settings page
# ===========================================================================

def load_preferences(user_id: str = "default") -> UserPreferences:
    """
    Load user preferences, returning defaults if none exist.

    Args:
        user_id (str): The user's UUID (defaults to 'default' for single-user mode).

    Returns:
        UserPreferences: The user's stored preferences (or fresh defaults).

    Used by: WellnessAgent (reads schedule preferences),
             RecommendationAgent (personalises suggestions),
             Settings page (displays and edits preferences)
    """
    prefs_list = db.read_all(UserPreferences, _PREFERENCES_FILE)
    for pref in prefs_list:
        if pref.user_id == user_id:
            return pref
    # Return defaults if no preferences saved yet
    return UserPreferences(user_id=user_id)


def save_preferences(preferences: UserPreferences) -> UserPreferences:
    """
    Save or update user preferences.

    Args:
        preferences (UserPreferences): The preferences object to save.

    Returns:
        UserPreferences: The saved preferences.

    Used by: Settings page (user updates preferences)
    """
    prefs_list = db.read_all(UserPreferences, _PREFERENCES_FILE)
    # Replace existing or append new
    prefs_list = [p for p in prefs_list if p.user_id != preferences.user_id]
    prefs_list.append(preferences)
    db.write_all(prefs_list, _PREFERENCES_FILE)
    logger.info(f"[save_preferences] Saved preferences for user {preferences.user_id}")
    return preferences
