"""
agents/intake_agent.py — Intake Agent
=======================================
Responsibility:
    The first agent in the NeuroMate pipeline.
    Receives raw user input, validates and structures it, then
    passes a clean, normalized payload to the PriorityAgent.

Input:
    Raw user-provided text describing tasks, goals, or concerns.

Output:
    A structured dictionary containing:
        - extracted_tasks: list of identified tasks
        - extracted_events: list of identified calendar events
        - raw_intent: the user's apparent goal
        - confidence: agent's confidence score (0.0 – 1.0)

Calls MCP Tools:
    - add_task()  → when a new task is extracted from user input
    - add_event() → when a new event is extracted from user input

Future Integration:
    - Use Gemini to extract tasks and events via NLP.
    - Classify intent (planning, venting, asking, scheduling).
"""

from utils import get_logger

logger = get_logger(__name__)


class IntakeAgent:
    """
    Parses and structures raw user input for the NeuroMate pipeline.

    This agent acts as the entry point. It is responsible for:
        1. Accepting free-form user input.
        2. Identifying tasks, events, and user intent.
        3. Normalising the data into a structured format.
        4. Handing off to PriorityAgent.

    Attributes:
        name (str): Human-readable agent name.
        version (str): Agent version for logging and debugging.
    """

    name: str = "Intake Agent"
    version: str = "0.1.0"

    def __init__(self):
        logger.info(f"[{self.name}] Initialized (v{self.version})")

    def process(self, user_input: str) -> dict:
        """
        Main entry point. Parse user input and return structured payload.

        Args:
            user_input (str): Raw text from the user.

        Returns:
            dict: Structured payload with keys:
                  - 'extracted_tasks' (list[dict])
                  - 'extracted_events' (list[dict])
                  - 'raw_intent' (str)
                  - 'raw_input' (str)
                  - 'confidence' (float)

        TODO (Phase 2): Replace placeholder logic with Gemini NLP extraction.
        """
        logger.info(f"[{self.name}] Processing input: '{user_input[:60]}...'")
        structured = self._structure_input(user_input)
        validated = self._validate(structured)
        return validated

    def _structure_input(self, user_input: str) -> dict:
        """
        Convert raw text into a structured dictionary.

        TODO (Phase 2): Call Gemini with a structured extraction prompt.
                        Return JSON with tasks, events, and intent fields.

        Args:
            user_input (str): Raw user text.

        Returns:
            dict: Partially structured data (placeholder implementation).
        """
        # Placeholder: return the input as-is with empty extractions
        return {
            "extracted_tasks": [],    # Will be populated by Gemini
            "extracted_events": [],   # Will be populated by Gemini
            "raw_intent": "unknown",  # e.g. 'planning', 'venting', 'asking'
            "raw_input": user_input,
            "confidence": 0.0,        # Gemini will provide a confidence score
        }

    def _validate(self, structured: dict) -> dict:
        """
        Validate the structured payload before passing downstream.

        Ensures required keys are present and data types are correct.

        Args:
            structured (dict): Output of _structure_input().

        Returns:
            dict: Validated (and potentially corrected) payload.
        """
        required_keys = ["extracted_tasks", "extracted_events", "raw_intent", "raw_input"]
        for key in required_keys:
            if key not in structured:
                logger.warning(f"[{self.name}] Missing key '{key}' — inserting default.")
                structured[key] = [] if "tasks" in key or "events" in key else ""
        return structured
