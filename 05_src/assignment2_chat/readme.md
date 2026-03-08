# Chef Byte - AI Chef Assistant

## Overview

**Chef Byte** is a conversational AI assistant with a passionate, Italian-inspired chef personality. It helps users discover recipes, learn about food science and nutrition, and explore the latest food trends — all through a fun, engaging Gradio chat interface.

## Personality

Chef Byte speaks with the flair of an Italian grandmother who also happens to be a tech genius. It uses food metaphors, Italian expressions (*Bellissimo! Mangia!*), and addresses users warmly as "friend" or "amico." It is enthusiastic, theatrical, and genuinely excited about all things food.

## Services

### Service 1: Recipe Search (API)
- **Backend**: [TheMealDB API](https://www.themealdb.com/api.php) (free, no API key required)
- **Functionality**: Search recipes by name, by ingredient, or get a random recipe
- **Response handling**: Raw API data is transformed into natural conversational text (not returned verbatim). The LLM first extracts search intent (name/ingredient/random), queries the API, formats the structured data, and then Chef Byte rephrases it in its personality.

### Service 2: Food Knowledge Base (Semantic Search)
- **Backend**: ChromaDB with file persistence + OpenAI embeddings (`text-embedding-3-small`)
- **Dataset**: 25 curated food/nutrition/cooking technique documents covering topics like the Maillard reaction, omega-3 fatty acids, knife skills, fermentation, and more
- **Embedding process**: Run `python -m services.build_knowledge_base` once to generate embeddings via the OpenAI API and store them in a local ChromaDB instance at `./data/chroma_db/`.
- **Search**: User queries are embedded and compared against the knowledge base using cosine similarity. The top 3 results are returned as context for the LLM.

### Service 3: Web Search (OpenAI Web Search Tool)
- **Backend**: OpenAI Responses API with `web_search_preview` tool
- **Functionality**: Searches the web for current food trends, restaurant recommendations, food news, and any food-related topics requiring up-to-date information

## Implementation Decisions

### Intent Classification
An LLM-based intent classifier routes user messages to the appropriate service:
- `recipe` -> TheMealDB API
- `knowledge` -> ChromaDB semantic search
- `web_search` -> OpenAI web search
- `general` -> Direct LLM response with personality

### Memory Management
- The system maintains a sliding window of the last 20 conversation turns (40 messages)
- When the window is exceeded, older messages are trimmed with a summary note indicating that earlier context was removed
- This prevents context window overflow while maintaining conversational continuity

### Guardrails
- **Restricted topics**: Cats, dogs, horoscopes, zodiac signs, and Taylor Swift are blocked via regex pattern matching. The system responds with a playful food-themed deflection.
- **Prompt injection protection**: Attempts to reveal, modify, or bypass the system prompt are detected via regex patterns and met with a humorous refusal.
- Both guardrails are applied before any service routing or LLM calls.

### API Key Management
- API keys are loaded from `05_src/.secrets` using `python-dotenv`, consistent with the course standard setup.
- The system tries `API_GATEWAY_KEY` first, then falls back to `OPENAI_API_KEY`.

## Setup & Running

### Prerequisites
- Python environment with the course standard libraries (`openai`, `chromadb`, `gradio`, `requests`, `python-dotenv`)
- `.secrets` file in `05_src/` directory with your API key (already provided in the course setup)

### Steps

1. **Verify your `.secrets` file exists at `05_src/.secrets`** with at least:
   ```
   API_GATEWAY_KEY=your-key-here
   ```

2. **Build the knowledge base (run once):**
   ```bash
   cd 05_src/assignment2_chat
   python -m services.build_knowledge_base
   ```

3. **Launch the app:**
   ```bash
   python app.py
   ```

4. Open the Gradio URL shown in the terminal (typically `http://127.0.0.1:7860`)

## File Structure

```
assignment2_chat/
├── app.py                          # Main entry point (Gradio UI)
├── config.py                       # Configuration and secrets loading
├── readme.md                       # This file
├── chat/
│   ├── __init__.py
│   ├── interface.py                # Message routing and response generation
│   ├── memory.py                   # Conversation memory (sliding window)
│   └── personality.py              # System prompt loading
├── data/
│   └── chroma_db/                  # ChromaDB persistent storage
├── guardrails/
│   ├── __init__.py
│   └── filters.py                  # Topic and injection filters
├── prompts/
│   └── system_prompt.txt           # Chef Byte's system prompt
├── services/
│   ├── __init__.py
│   ├── api_service.py              # Service 1: TheMealDB recipe search
│   ├── build_knowledge_base.py     # One-time embedding script
│   ├── semantic_search_service.py  # Service 2: ChromaDB semantic search
│   └── web_search_service.py       # Service 3: OpenAI web search
└── utils/
    ├── __init__.py
    └── helpers.py                  # Environment checks
```

## Libraries Used
- `openai` — LLM and embeddings
- `chromadb` — Vector database with file persistence
- `gradio` — Chat interface
- `requests` — HTTP API calls
- `python-dotenv` — Loading `.secrets` file