"""
Chef Byte's personality and system prompt management.
"""

import os


def load_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts",
        "system_prompt.txt",
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_system_message() -> dict:
    """Return the system message dict for OpenAI API."""
    return {"role": "system", "content": load_system_prompt()}