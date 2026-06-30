"""
agents/scheduler_agent.py — Scheduler Agent
=============================================
Responsibility:
    Converts a ranked list of tasks into a time-blocked daily schedule.
    Checks the user's calendar for existing events to avoid conflicts.

Input:
    Enriched pipeline payload from PriorityAgent, including ranked tasks.

Output:
    The payload, further enriched with:
        - schedule: list of ScheduleBlock objects for the day
        - conflicts: list of any detected time conflicts
        - schedule_summary: human-readable summary of the plan

Calls MCP Tools:
    - get_tasks()  → reads pending tasks to schedule
    - get_events() → reads existing calendar events for conflict detection
    - add_event()  → persists AI-generated schedule blocks as events

Calls Scheduler Module:
    - scheduler.generate_schedule()
    - scheduler.detect_conflicts()
    - scheduler.recommend_breaks()

Future Integration:
    - Use Gemini to assign realistic time estimates to tasks.
    - Adapt schedule to user's work hours from UserPreferences.
"""

import mcp_server as mcp
import scheduler as sched
from utils import get_logger

logger = get_logger(__name__)


class SchedulerAgent:
    """
    Builds a conflict-free, time-blocked daily plan.

    This agent sits between PriorityAgent and WellnessAgent.
    It takes ranked tasks, checks available calendar slots,
    and produces an ordered schedule the user can act on.

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Scheduler Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, priority_payload: dict) -> dict:
        """
        Generate and validate a daily schedule.

        Args:
            priority_payload (dict): Output from PriorityAgent.process().

        Returns:
            dict: Priority payload enriched with schedule data.
        """
        logger.info(f"[{self.name}] Generating daily schedule.")

        tasks = mcp.get_tasks(status="pending")
        events = mcp.get_events()

        raw_schedule = sched.generate_schedule(tasks=tasks, events=events)
        optimized = sched.optimize_schedule(raw_schedule)
        with_breaks = sched.recommend_breaks(optimized)
        conflicts = sched.detect_conflicts(with_breaks)

        summary = self._summarize_schedule(with_breaks, conflicts)

        return {
            **priority_payload,
            "schedule": [block.to_dict() for block in with_breaks],
            "conflicts": conflicts,
            "schedule_summary": summary,
        }

    def generate_daily_schedule(self) -> list:
        """
        Public helper: generate today's schedule independently.

        Returns:
            list[dict]: Schedule blocks as dictionaries.

        Usage:
            agent = SchedulerAgent()
            schedule = agent.generate_daily_schedule()
        """
        tasks = mcp.get_tasks(status="pending")
        events = mcp.get_events()
        blocks = sched.generate_schedule(tasks=tasks, events=events)
        return [b.to_dict() for b in blocks]

    def _summarize_schedule(self, schedule: list, conflicts: list) -> str:
        """
        Generate a short human-readable summary of the schedule.

        TODO (Phase 2): Use Gemini to write a personalized, natural-language
                        summary that highlights key blocks and warns about conflicts.

        Args:
            schedule (list): List of ScheduleBlock objects.
            conflicts (list): List of conflict records.

        Returns:
            str: Schedule summary text.
        """
        block_count = len(schedule)
        conflict_msg = f" ⚠️ {len(conflicts)} conflict(s) detected." if conflicts else ""
        return (
            f"Your day has {block_count} scheduled block(s).{conflict_msg} "
            "AI scheduling optimization will be available in the next version."
        )
