"""
Guardrails for Chef Byte.
Blocks restricted topics and prompt injection attempts.
"""

import re

# Topics that are restricted
RESTRICTED_PATTERNS = [
    # Cats and dogs
    r"\b(cat|cats|kitten|kittens|feline|felines|meow)\b",
    r"\b(dog|dogs|puppy|puppies|canine|canines|bark|woof)\b",
    # Horoscopes and zodiac
    r"\b(horoscope|horoscopes|zodiac|astrology|astrological)\b",
    r"\b(aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b",
    # Taylor Swift
    r"\b(taylor\s*swift|t[\.\s]*swift|tswift)\b",
]

# Patterns that try to extract or modify system prompt
PROMPT_INJECTION_PATTERNS = [
    r"(system\s*prompt|system\s*message|system\s*instruction)",
    r"(ignore\s*(previous|all|prior|above)\s*(instruction|prompt|rule))",
    r"(reveal|show|display|print|output|repeat)\s*(your|the|my)?\s*(system|initial|original|hidden)\s*(prompt|instruction|message|rule)",
    r"(what\s*(are|is)\s*your\s*(instruction|prompt|rule|system))",
    r"(pretend|act\s*as\s*if|roleplay)\s*(you\s*(are|have)\s*no\s*rule)",
    r"(forget|disregard|override)\s*(your|all|the)?\s*(rule|instruction|prompt)",
    r"(tell\s*me\s*(your|the)\s*(rule|instruction|prompt|system))",
    r"(repeat\s*(everything|all)\s*(above|before|from\s*the\s*start))",
]

RESTRICTED_RESPONSE = (
    "Ah, amico! 🍝 That topic is not on my menu, I'm afraid! "
    "I'm Chef Byte — I live and breathe food, recipes, and all things delicious. "
    "How about we talk about something tasty instead? "
    "Ask me for a recipe, a nutrition fact, or the latest food trends! Mangia! 🍕"
)

PROMPT_INJECTION_RESPONSE = (
    "Ha! Nice try, my dear friend! 😄🍳 "
    "A good chef never reveals their secret recipe, and this chef never reveals their secret instructions! "
    "Now, let's get back to what matters — FOOD! "
    "What can I cook up for you today? 🍲"
)


def check_restricted_topics(user_message: str) -> str | None:
    """
    Check if the user message contains restricted topics.
    Returns a rejection message if restricted, None if clean.
    """
    text = user_message.lower().strip()
    for pattern in RESTRICTED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return RESTRICTED_RESPONSE
    return None


def check_prompt_injection(user_message: str) -> str | None:
    """
    Check if the user is trying to access or modify the system prompt.
    Returns a rejection message if detected, None if clean.
    """
    text = user_message.lower().strip()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return PROMPT_INJECTION_RESPONSE
    return None


def apply_guardrails(user_message: str) -> str | None:
    """
    Apply all guardrails. Returns a rejection message if any guardrail
    is triggered, or None if the message is acceptable.
    """
    # Check prompt injection first (higher priority)
    result = check_prompt_injection(user_message)
    if result:
        return result

    # Check restricted topics
    result = check_restricted_topics(user_message)
    if result:
        return result

    return None