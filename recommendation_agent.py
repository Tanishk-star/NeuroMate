"""
agents/recommendation_agent.py — Recommendation Agent
=======================================================
Responsibility:
    Synthesises data from all upstream agents (tasks, schedule, wellness)
    to generate personalised, context-aware recommendations for the user.

Input:
    Enriched pipeline payload from WellnessAgent, containing the full
    picture of the user's tasks, schedule, and wellness status.

Output:
    The payload, further enriched with:
        - recommendations: list of personalised recommendation objects
        - daily_tip: a single motivational tip for the day
        - focus_task: the single most important task to focus on

Calls MCP Tools:
    - get_tasks()        → reads task list for context
    - load_preferences() → personalises recommendations to user style

Future Integration:
    - Use Gemini to generate rich, natural-language recommendations.
    - Tailor tone to the user's selected buddy_personality.
    - Incorporate wellness flags, stress level, and mood trends.
"""

import mcp_server as mcp
from utils import get_logger

logger = get_logger(__name__)

# Placeholder daily tips — will be replaced by Gemini-generated content
_PLACEHOLDER_TIPS = [
    "🌟 Focus on progress, not perfection.",
    "🧠 Protect your peak energy hours for your most important work.",
    "📵 Single-tasking beats multitasking every time.",
    "🚶 A short walk can reset your focus better than coffee.",
    "📝 Capture every thought — your brain is for thinking, not storing.",
]


class RecommendationAgent:
    """
    Generates personalised recommendations from synthesised pipeline data.

    This agent is the final intelligence step before the ReflectionAgent.
    It takes all gathered context and produces concrete, actionable advice
    tailored to the user's preferences and current situation.

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Recommendation Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, wellness_payload: dict) -> dict:
        """
        Generate recommendations from the enriched pipeline payload.

        Args:
            wellness_payload (dict): Output from WellnessAgent.process().

        Returns:
            dict: Wellness payload enriched with recommendation data.
        """
        logger.info(f"[{self.name}] Generating personalised recommendations.")

        preferences = mcp.load_preferences()
        tasks = mcp.get_tasks(status="pending")

        recommendations = self._build_recommendations(wellness_payload, preferences)
        daily_tip = self._select_daily_tip(preferences)
        focus_task = self._identify_focus_task(tasks)

        return {
            **wellness_payload,
            "recommendations": recommendations,
            "daily_tip": daily_tip,
            "focus_task": focus_task,
        }

    def _build_recommendations(self, payload: dict, preferences) -> list[dict]:
        """
        Build a list of recommendation objects from the current pipeline state.

        TODO (Phase 2): Use Gemini to generate recommendations based on:
            - Stress level (from WellnessAgent)
            - Wellness suggestions (from WellnessAgent)
            - Buddy personality (from UserPreferences)
            - Time of day / day of week

        Args:
            payload (dict): The full enriched pipeline payload.
            preferences: UserPreferences object.

        Returns:
            list[dict]: Recommendation objects with 'category', 'text', 'priority'.
        """
        recommendations = []
        stress = payload.get("stress_level_estimate", "low")
        wellness_suggestions = payload.get("wellness_suggestions", [])

        # Convert wellness suggestions into recommendation objects
        for suggestion in wellness_suggestions:
            recommendations.append({
                "category": "wellness",
                "text": suggestion,
                "priority": "high" if stress == "high" else "medium",
            })

        # Placeholder general recommendation
        recommendations.append({
            "category": "productivity",
            "text": "📅 Review your top 3 tasks each morning to stay aligned with your goals.",
            "priority": "medium",
        })

        return recommendations

    def _select_daily_tip(self, preferences) -> str:
        """
        Select or generate a motivational tip for the day.

        TODO (Phase 2): Use Gemini to generate a tip tailored to the
                        user's buddy_personality and current stress level.

        Args:
            preferences: UserPreferences object.

        Returns:
            str: A single motivational tip.
        """
        from datetime import datetime
        # Use day of year to rotate through tips consistently
        day_index = datetime.now().timetuple().tm_yday % len(_PLACEHOLDER_TIPS)
        return _PLACEHOLDER_TIPS[day_index]

    def _identify_focus_task(self, tasks: list) -> dict:
        """
        Identify the single highest-priority task to highlight.

        TODO (Phase 2): Use Gemini to select the focus task considering
                        deadlines, task complexity, and user energy levels.

        Args:
            tasks (list): List of Task objects from the MCP tool layer.

        Returns:
            dict: The focus task as a dictionary, or an empty dict if no tasks.
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}
        if not tasks:
            return {}
        top_task = min(tasks, key=lambda t: priority_order.get(t.priority, 1))
        return {
            "id": top_task.id,
            "title": top_task.title,
            "priority": top_task.priority,
            "due_date": top_task.due_date,
        }
