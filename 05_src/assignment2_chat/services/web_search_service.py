"""
Service 3: Web Search using OpenAI's web search tool.
Allows users to search for trending food topics, restaurant info, etc.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import get_openai_client, CHAT_MODEL


def handle_web_search(user_message: str) -> str:
    """
    Perform a web search using the OpenAI Responses API with web_search tool.
    Returns a summarized response.
    """
    client = get_openai_client()

    try:
        response = client.responses.create(
            model=CHAT_MODEL,
            tools=[{"type": "web_search_preview"}],
            input=user_message,
        )

        # Extract text from the response
        result_text = ""
        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if content.type == "output_text":
                        result_text += content.text

        if not result_text:
            return "I searched the web but couldn't find anything useful. Try rephrasing your question!"

        return result_text

    except Exception as e:
        return f"Web search encountered an issue: {str(e)}. Let me try to answer from what I know instead!"