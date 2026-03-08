"""
Service 2: Semantic Search over food knowledge base using ChromaDB.
Uses OpenAI embeddings to find the most relevant documents.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import chromadb
from config import (
    get_openai_client,
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


def get_collection():
    """Get the ChromaDB collection."""
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)


def semantic_search(query: str, n_results: int = 3) -> list[dict]:
    """
    Perform semantic search over the food knowledge base.

    Args:
        query: User's question
        n_results: Number of results to return

    Returns:
        List of dicts with 'text', 'topic', and 'distance' keys
    """
    client = get_openai_client()

    # Generate query embedding
    response = client.embeddings.create(
        input=[query],
        model=EMBEDDING_MODEL,
    )
    query_embedding = response.data[0].embedding

    # Query ChromaDB
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    # Format results
    formatted = []
    for i in range(len(results["documents"][0])):
        formatted.append({
            "text": results["documents"][0][i],
            "topic": results["metadatas"][0][i].get("topic", "general"),
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })

    return formatted


def handle_knowledge_query(user_message: str) -> str:
    """
    Main entry point for the semantic search service.
    Searches the knowledge base and returns relevant context.
    """
    try:
        results = semantic_search(user_message, n_results=3)

        if not results:
            return "I couldn't find anything relevant in my knowledge base. Could you rephrase your question?"

        # Build context from search results
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i} — Topic: {r['topic']}]\n{r['text']}"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        return (
            f"My knowledge base seems to be taking a nap! Error: {str(e)}. "
            "Have you run: python -m services.build_knowledge_base ?"
        )