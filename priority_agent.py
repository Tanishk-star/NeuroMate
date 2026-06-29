"""
agents/priority_agent.py — Priority Agent
==========================================
Responsibility:
    Receives structured task data from the IntakeAgent and assigns
    intelligent priority scores based on urgency, importance, and
    user context.

Input:
    Structured payload from IntakeAgent containing extracted tasks.

Output:
    The same payload, enriched with:
        - priority_scores: dict mapping task ID → priority level
        - ranked_tasks: list of tasks sorted by computed priority
        - reasoning: short explanation of ranking decisions

Calls MCP Tools:
    - get_tasks()    → reads existing tasks to avoid duplicates and
                       understand current workload
    - update_task()  → writes computed priority back to the task record

Future Integration:
    - Use Gemini to apply the Eisenhower Matrix (urgent/important).
    - Consider user energy levels and deadlines from context.
"""

import mcp_server as mcp
from utils import get_logger

logger = get_logger(__name__)


class PriorityAgent:
    """
    Assigns and updates task priorities within the NeuroMate pipeline.

    Implements a ranking step between intake (parsing) and scheduling
    (time blocking), ensuring the most impactful tasks are surfaced first.

    Priority Levels:
        - 'high'   → urgent AND important (do immediately)
        - 'medium' → important but not urgent (schedule deliberately)
        - 'low'    → neither urgent nor important (batch or defer)

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Priority Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, intake_payload: dict) -> dict:
        """
        Rank tasks by priority and enrich the pipeline payload.

        Args:
            intake_payload (dict): Output from IntakeAgent.process().

        Returns:
            dict: Intake payload enriched with priority data.
        """
        logger.info(f"[{self.name}] Ranking tasks from intake payload.")
        tasks = intake_payload.get("extracted_tasks", [])
        existing_tasks = mcp.get_tasks(status="pending")

        ranked = self._rank_tasks(tasks, existing_tasks)
        reasoning = self._generate_reasoning(ranked)

        return {
            **intake_payload,
            "ranked_tasks": ranked,
            "priority_reasoning": reasoning,
        }

    def _rank_tasks(self, new_tasks: list, existing_tasks: list) -> list:
        """
        Apply priority scoring to a list of tasks.

        TODO (Phase 2): Use Gemini to apply Eisenhower Matrix analysis.
                        Consider due dates, user-defined urgency, and tags.

        Args:
            new_tasks (list): Tasks extracted by IntakeAgent (dicts).
            existing_tasks (list): Task objects from the MCP tool layer.

        Returns:
            list: Tasks sorted from highest to lowest priority.
        """
        # Placeholder: return tasks in original order
        priority_order = {"high": 0, "medium": 1, "low": 2}
        combined = new_tasks + [vars(t) if hasattr(t, '__dict__') else t for t in existing_tasks]
        return sorted(combined, key=lambda t: priority_order.get(t.get("priority", "medium"), 1))

    def _generate_reasoning(self, ranked_tasks: list) -> str:
        """
        Produce a human-readable explanation of the prioritization.

        TODO (Phase 2): Generate natural-language reasoning via Gemini,
                        explaining why each task was ranked as it was.

        Args:
            ranked_tasks (list): The ranked task list.

        Returns:
            str: Placeholder reasoning text.
        """
        count = len(ranked_tasks)
        return (
            f"Ranked {count} task(s) by priority level. "
            "AI-powered reasoning will be available in the next version."
        )
