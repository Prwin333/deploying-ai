"""
Conversation memory management.
Maintains chat history with a sliding window to manage context size.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import MAX_CONVERSATION_TURNS


class ConversationMemory:
    """Manages conversation history with a sliding window."""

    def __init__(self, max_turns: int = MAX_CONVERSATION_TURNS):
        self.max_turns = max_turns
        self.history: list[dict] = []  # list of {"role": ..., "content": ...}

    def add_user_message(self, message: str):
        """Add a user message to history."""
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant_message(self, message: str):
        """Add an assistant message to history."""
        self.history.append({"role": "assistant", "content": message})
        self._trim()

    def get_history(self) -> list[dict]:
        """Return the current conversation history."""
        return list(self.history)

    def _trim(self):
        """
        Trim conversation to stay within max_turns.
        Each 'turn' is a user+assistant pair (2 messages).
        We keep the most recent turns and add a summary note.
        """
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            overflow = len(self.history) - max_messages
            summary_note = {
                "role": "system",
                "content": (
                    f"[Note: {overflow // 2} earlier conversation turns were trimmed "
                    "to manage context. The conversation continues below.]"
                ),
            }
            self.history = [summary_note] + self.history[-max_messages:]

    def clear(self):
        """Clear all history."""
        self.history = []

    def get_turn_count(self) -> int:
        """Return the approximate number of conversation turns."""
        return len([m for m in self.history if m["role"] == "user"])