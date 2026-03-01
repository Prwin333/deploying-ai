"""
Utility helpers for the Chef Byte application.
"""

import os


def check_environment():
    """Check that required configuration is available."""
    issues = []

    secrets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".secrets"
    )

    if os.path.exists(secrets_path):
        issues.append("  .secrets file found.")
    else:
        issues.append("  .secrets file NOT found in 05_src/ directory.")
        return issues

    try:
        from config import API_GATEWAY_KEY, OPENAI_API_KEY
        key = API_GATEWAY_KEY or OPENAI_API_KEY
        if key:
            masked = key[:4] + "..." + key[-4:]
            issues.append(f"  API key loaded: {masked}")
        else:
            issues.append("  No API key found in .secrets file.")
    except Exception as e:
        issues.append(f"  Error loading config: {e}")

    return issues


def check_knowledge_base():
    """Check if the ChromaDB knowledge base exists."""
    from config import CHROMA_PERSIST_DIR

    chroma_path = os.path.join(CHROMA_PERSIST_DIR, "chroma.sqlite3")
    if os.path.exists(chroma_path):
        return "  Knowledge base exists."
    else:
        return "  Knowledge base NOT found. Run: python -m services.build_knowledge_base"