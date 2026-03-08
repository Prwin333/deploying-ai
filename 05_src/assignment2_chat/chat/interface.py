"""
Chat interface logic for Chef Byte.
Routes user messages to appropriate services and manages conversation.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import get_openai_client, CHAT_MODEL
from chat.personality import get_system_message
from chat.memory import ConversationMemory
from guardrails.filters import apply_guardrails
from services.api_service import handle_recipe_query
from services.semantic_search_service import handle_knowledge_query
from services.web_search_service import handle_web_search


# Global memory instance
memory = ConversationMemory()


def classify_intent(user_message: str) -> str:
    """
    Use the LLM to classify the user's intent into one of the services.
    Returns: 'recipe', 'knowledge', 'web_search', or 'general'
    """
    client = get_openai_client()

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an intent classifier for a food/cooking chatbot. "
                    "Classify the user message into ONE of these categories:\n"
                    "- 'recipe': User wants to find a recipe, search for a dish, or look up a meal by name/ingredient.\n"
                    "- 'knowledge': User asks about nutrition, food science, cooking techniques, ingredients, or food facts.\n"
                    "- 'web_search': User asks about current food trends, restaurant recommendations, food news, or anything that requires up-to-date web information.\n"
                    "- 'general': Casual conversation, greetings, or anything that doesn't fit the above.\n\n"
                    "Return ONLY the category name, nothing else."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )

    intent = response.choices[0].message.content.strip().lower()
    if intent not in ("recipe", "knowledge", "web_search", "general"):
        intent = "general"

    return intent


def generate_response(user_message: str) -> str:
    """
    Main function to process a user message and generate a response.
    """
    # 1. Apply guardrails
    guardrail_response = apply_guardrails(user_message)
    if guardrail_response:
        memory.add_user_message(user_message)
        memory.add_assistant_message(guardrail_response)
        return guardrail_response

    # 2. Classify intent
    intent = classify_intent(user_message)

    # 3. Get service-specific context
    service_context = ""

    if intent == "recipe":
        service_context = handle_recipe_query(user_message)
        service_context = (
            f"\n\n[RECIPE SEARCH RESULTS]\n{service_context}\n[END RESULTS]\n\n"
            "Use the above recipe information to respond to the user in your Chef Byte personality. "
            "Rephrase and present the information naturally."
        )

    elif intent == "knowledge":
        service_context = handle_knowledge_query(user_message)
        service_context = (
            f"\n\n[KNOWLEDGE BASE RESULTS]\n{service_context}\n[END RESULTS]\n\n"
            "Use the above information to answer the user's question in your Chef Byte personality. "
            "Synthesize and rephrase the information naturally."
        )

    elif intent == "web_search":
        service_context = handle_web_search(user_message)
        service_context = (
            f"\n\n[WEB SEARCH RESULTS]\n{service_context}\n[END RESULTS]\n\n"
            "Use the above web search results to respond to the user in your Chef Byte personality. "
            "Summarize and present the information engagingly."
        )

    # 4. Add user message to memory
    memory.add_user_message(user_message)

    # 5. Build messages for the LLM
    messages = [get_system_message()]
    messages.extend(memory.get_history())

    # Add service context as a system hint (not visible in history)
    if service_context:
        messages.append({"role": "system", "content": service_context})

    # 6. Generate response
    client = get_openai_client()
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=1000,
    )

    assistant_message = response.choices[0].message.content

    # 7. Save assistant response to memory
    memory.add_assistant_message(assistant_message)

    return assistant_message


def reset_conversation():
    """Clear the conversation memory."""
    memory.clear()