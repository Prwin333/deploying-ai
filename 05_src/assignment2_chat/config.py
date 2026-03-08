"""
Configuration settings for Chef Byte — AI Chef Assistant.
Loads API keys from 05_src/.secrets using python-dotenv.
Uses the UofT API Gateway for OpenAI access.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load secrets from .secrets file in 05_src/ directory
_secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".secrets")
load_dotenv(_secrets_path)

# API Gateway configuration (UofT course setup)
API_GATEWAY_KEY = os.environ.get("API_GATEWAY_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_GATEWAY_BASE_URL = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1"


def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client.
    Uses the API Gateway if API_GATEWAY_KEY is set, otherwise falls back to direct OpenAI key.
    """
    if API_GATEWAY_KEY:
        return OpenAI(
            base_url=API_GATEWAY_BASE_URL,
            api_key=API_GATEWAY_KEY,
            default_headers={"x-api-key": API_GATEWAY_KEY},
        )
    elif OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY)
    else:
        raise ValueError(
            "Neither API_GATEWAY_KEY nor OPENAI_API_KEY found. "
            f"Check your .secrets file at: {_secrets_path}"
        )


# Model settings
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# ChromaDB settings
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")
CHROMA_COLLECTION_NAME = "food_knowledge"

# TheMealDB API (free, no key required)
MEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Memory settings
MAX_CONVERSATION_TURNS = 20  # keep last N user+assistant turn pairs