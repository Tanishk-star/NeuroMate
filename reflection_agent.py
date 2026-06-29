"""
agents/reflection_agent.py — Reflection Agent
===============================================
Responsibility:
    The final agent in the NeuroMate pipeline.
    Synthesises the full pipeline output into a coherent, friendly
    final response for the user. Also supports end-of-day reflection
    by analysing journal entries and generating insights.

Input:
    The fully enriched pipeline payload from RecommendationAgent.

Output:
    A final response object containing:
        - final_message: the complete user-facing response text
        - action_items: a concise list of next steps for the user
        - pipeline_summary: a structured summary of all agent outputs

Calls MCP Tools:
    - load_journal()     → reads recent journal entries for mood trends
    - save_journal()     → persists the user's reflection (journal page only)

Security Note:
    Journal access through this agent must only occur when the user
    has authenticated via the Journal page password gate. The agent
    itself does not enforce the password — that is the UI's responsibility.

Future Integration:
    - Use Gemini to compose empathetic, personalised final responses.
    - Generate weekly/monthly reflection summaries from journal trends.
    - Adapt tone to the user's selected buddy_personality.
"""

import mcp_server as mcp
from utils import get_logger

logger = get_logger(__name__)


class ReflectionAgent:
    """
    Composes the final user-facing response and supports journaling.

    This agent acts as the NeuroMate 'voice' — it takes everything the
    other agents have computed and translates it into a human message.

    It also powers the Journal feature by:
        1. Accepting the user's daily reflection.
        2. Optionally analysing past entries for mood trends.
        3. Generating an end-of-day summary.

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Reflection Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, recommendation_payload: dict) -> dict:
        """
        Compose the final pipeline response from all agent outputs.

        Args:
            recommendation_payload (dict): Output from RecommendationAgent.process().

        Returns:
            dict: Final response payload with user-facing content.
        """
        logger.info(f"[{self.name}] Composing final pipeline response.")

        final_message = self._compose_final_message(recommendation_payload)
        action_items = self._extract_action_items(recommendation_payload)
        summary = self._build_pipeline_summary(recommendation_payload)

        return {
            **recommendation_payload,
            "final_message": final_message,
            "action_items": action_items,
            "pipeline_summary": summary,
        }

    def _compose_final_message(self, payload: dict) -> str:
        """
        Write the complete user-facing response message.

        TODO (Phase 2): Use Gemini to compose a natural, empathetic message
                        that reflects the user's buddy_personality setting,
                        stress level, and the day's key recommendations.

        Args:
            payload (dict): The fully enriched pipeline payload.

        Returns:
            str: The final message to display to the user.
        """
        daily_tip = payload.get("daily_tip", "")
        stress = payload.get("stress_level_estimate", "low")
        schedule_summary = payload.get("schedule_summary", "")

        stress_note = {
            "low": "You're set up for a productive day! 💪",
            "moderate": "Your schedule is busy — remember to pace yourself. 🌿",
            "high": "Your plate looks full today. Let's focus on what matters most. 🧘",
        }.get(stress, "")

        return (
            f"👋 Here's your NeuroMate briefing!\n\n"
            f"{stress_note}\n\n"
            f"📅 **Schedule**: {schedule_summary}\n\n"
            f"💡 **Today's Tip**: {daily_tip}\n\n"
            f"_AI-powered personalisation coming in the next version._"
        )

    def _extract_action_items(self, payload: dict) -> list[str]:
        """
        Distil the pipeline output into a short list of next steps.

        TODO (Phase 2): Use Gemini to intelligently rank and phrase action
                        items based on priority, deadline, and user energy.

        Args:
            payload (dict): The fully enriched pipeline payload.

        Returns:
            list[str]: Concise, actionable next steps (max 5 items).
        """
        items = []
        focus_task = payload.get("focus_task", {})
        if focus_task:
            items.append(f"🎯 Focus on: **{focus_task.get('title', 'Your top task')}**")

        recommendations = payload.get("recommendations", [])
        for rec in recommendations[:3]:   # Show at most 3 recommendations
            items.append(f"• {rec.get('text', '')}")

        return items

    def _build_pipeline_summary(self, payload: dict) -> dict:
        """
        Build a structured debug summary of all agent outputs.

        This is useful for the Insights page and for debugging the
        multi-agent pipeline during development.

        Args:
            payload (dict): The fully enriched pipeline payload.

        Returns:
            dict: A structured summary with keys per agent stage.
        """
        return {
            "tasks_found": len(payload.get("extracted_tasks", [])),
            "ranked_tasks": len(payload.get("ranked_tasks", [])),
            "schedule_blocks": len(payload.get("schedule", [])),
            "conflicts_detected": len(payload.get("conflicts", [])),
            "wellness_flags": len(payload.get("wellness_flags", [])),
            "recommendations_generated": len(payload.get("recommendations", [])),
            "stress_level": payload.get("stress_level_estimate", "unknown"),
        }

    # -----------------------------------------------------------------------
    # Journal Support Methods
    # -----------------------------------------------------------------------

    def save_daily_reflection(
        self, date: str, content: str, mood: str = "neutral"
    ):
        """
        Persist a user's daily journal reflection via the MCP tool layer.

        Security Note:
            This method must only be called AFTER the user has authenticated
            on the Journal page. The UI enforces the password gate.

        Args:
            date (str): ISO 8601 date string for the entry.
            content (str): The reflection text.
            mood (str): Mood tag for the entry.

        Returns:
            JournalEntry: The saved entry.
        """
        logger.info(f"[{self.name}] Saving journal entry for {date}")
        return mcp.save_journal(date=date, content=content, mood=mood)

    def load_recent_reflections(self, days: int = 7) -> list:
        """
        Load recent journal entries for mood trend analysis.

        Security Note:
            Only accessible through the authenticated Journal page.

        TODO (Phase 3): Use Gemini to analyse mood trends across entries
                        and generate weekly wellbeing insights.

        Args:
            days (int): Number of recent days to retrieve.

        Returns:
            list[JournalEntry]: Recent journal entries.
        """
        logger.info(f"[{self.name}] Loading last {days} days of journal entries.")
        return mcp.load_journal()  # Filtering by date range will be added in Phase 3
