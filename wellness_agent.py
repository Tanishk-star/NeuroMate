"""
agents/wellness_agent.py — Wellness Agent
==========================================
Responsibility:
    Monitors the user's schedule for signs of overload (too many tasks,
    insufficient breaks, long uninterrupted blocks) and injects wellness
    recommendations into the pipeline.

Input:
    Schedule payload from SchedulerAgent, including the time-blocked plan.

Output:
    The payload, enriched with:
        - wellness_flags: list of detected wellness concerns
        - wellness_suggestions: list of actionable recommendations
        - stress_level_estimate: 'low' | 'moderate' | 'high'

Calls MCP Tools:
    - load_preferences() → reads work hours and break interval settings

Future Integration:
    - Use Gemini to assess schedule density and generate personalized advice.
    - Integrate mood tracking from Journal entries via ReflectionAgent.
    - Apply evidence-based wellness heuristics (Pomodoro, 20-20-20 rule, etc.).
"""

import mcp_server as mcp
from utils import get_logger

logger = get_logger(__name__)

# Thresholds for wellness analysis
MAX_CONTINUOUS_WORK_MINUTES = 90
MIN_BREAK_DURATION_MINUTES = 10
HIGH_STRESS_TASK_COUNT = 8


class WellnessAgent:
    """
    Detects schedule overload and generates wellness recommendations.

    This agent acts as the user's wellbeing guardian in the pipeline.
    It does not modify the schedule but flags concerns and suggests
    adjustments for the user and the RecommendationAgent to act on.

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Wellness Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, schedule_payload: dict) -> dict:
        """
        Analyse the schedule for wellness concerns.

        Args:
            schedule_payload (dict): Output from SchedulerAgent.process().

        Returns:
            dict: Schedule payload enriched with wellness data.
        """
        logger.info(f"[{self.name}] Analysing schedule for wellness signals.")

        preferences = mcp.load_preferences()
        schedule = schedule_payload.get("schedule", [])

        flags = self._detect_wellness_flags(schedule, preferences)
        suggestions = self._generate_suggestions(flags, preferences)
        stress_level = self._estimate_stress_level(flags, schedule)

        return {
            **schedule_payload,
            "wellness_flags": flags,
            "wellness_suggestions": suggestions,
            "stress_level_estimate": stress_level,
        }

    def _detect_wellness_flags(self, schedule: list, preferences) -> list[str]:
        """
        Scan the schedule for wellness red flags.

        TODO (Phase 3): Apply evidence-based heuristics:
            - Continuous work blocks exceeding the break interval threshold.
            - No scheduled lunch break.
            - Tasks extending past end-of-day work hour.
            - More than HIGH_STRESS_TASK_COUNT tasks in a single day.

        Args:
            schedule (list): List of schedule block dictionaries.
            preferences: UserPreferences object.

        Returns:
            list[str]: Human-readable flag descriptions.
        """
        flags = []
        task_blocks = [b for b in schedule if b.get("block_type") == "task"]

        if len(task_blocks) >= HIGH_STRESS_TASK_COUNT:
            flags.append(f"⚠️ High task density: {len(task_blocks)} task blocks today.")

        # Placeholder: more checks will be added in Phase 3
        return flags

    def _generate_suggestions(self, flags: list[str], preferences) -> list[str]:
        """
        Create actionable wellness suggestions based on detected flags.

        TODO (Phase 3): Use Gemini to generate personalised, empathetic
                        wellness advice based on the specific flags and
                        the user's personality preference.

        Args:
            flags (list[str]): Wellness flags from _detect_wellness_flags().
            preferences: UserPreferences object.

        Returns:
            list[str]: Actionable suggestion strings.
        """
        suggestions = []
        if flags:
            suggestions.append(
                f"💧 Remember to drink water and take a {preferences.break_interval_minutes}-minute break every 90 minutes."
            )
            suggestions.append("🧘 Consider a 5-minute mindfulness break between heavy tasks.")
        else:
            suggestions.append("✅ Your schedule looks balanced. Great job planning ahead!")
        return suggestions

    def _estimate_stress_level(self, flags: list[str], schedule: list) -> str:
        """
        Estimate the user's potential stress level based on schedule density.

        TODO (Phase 3): Use a Gemini prompt to make a nuanced assessment
                        that considers task types, deadlines, and recent mood.

        Args:
            flags (list[str]): Detected wellness flags.
            schedule (list): Full schedule block list.

        Returns:
            str: 'low' | 'moderate' | 'high'
        """
        if len(flags) == 0:
            return "low"
        elif len(flags) <= 2:
            return "moderate"
        return "high"
