"""
Service 1: Recipe Search via TheMealDB API.
Searches for recipes by name or ingredient, then transforms
the raw API response into natural conversational text.
"""

import json
import requests

# Use a relative import path that works when running from the assignment2_chat dir
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MEALDB_BASE_URL, get_openai_client, CHAT_MODEL


def search_recipe_by_name(query: str) -> dict | None:
    """Search TheMealDB for a recipe by name."""
    try:
        url = f"{MEALDB_BASE_URL}/search.php"
        response = requests.get(url, params={"s": query}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def search_recipe_by_ingredient(ingredient: str) -> dict | None:
    """Search TheMealDB for recipes that use a given ingredient."""
    try:
        url = f"{MEALDB_BASE_URL}/filter.php"
        response = requests.get(url, params={"i": ingredient}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_random_recipe() -> dict | None:
    """Get a random recipe from TheMealDB."""
    try:
        url = f"{MEALDB_BASE_URL}/random.php"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def _format_meal_data(meal: dict) -> str:
    """Format a single meal dict into a readable string."""
    name = meal.get("strMeal", "Unknown")
    category = meal.get("strCategory", "N/A")
    area = meal.get("strArea", "N/A")
    instructions = meal.get("strInstructions", "No instructions available.")

    # Collect ingredients
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if ing and ing.strip():
            ingredients.append(f"  - {measure.strip()} {ing.strip()}")

    ingredients_str = "\n".join(ingredients) if ingredients else "  No ingredients listed."

    return (
        f"**{name}**\n"
        f"- Cuisine: {area}\n"
        f"- Category: {category}\n"
        f"- Ingredients:\n{ingredients_str}\n"
        f"- Instructions: {instructions[:500]}{'...' if len(instructions) > 500 else ''}"
    )


def format_recipe_results(data: dict) -> str:
    """Transform raw API data into a formatted text summary."""
    if not data or "error" in data:
        return "I couldn't find any recipes right now. The kitchen seems to be closed! Try again?"

    meals = data.get("meals")
    if not meals:
        return "No recipes found for that search. Maybe try a different ingredient or dish name?"

    # If it's a filter result (ingredient search), meals only have name + thumbnail
    if "strInstructions" not in meals[0]:
        names = [m.get("strMeal", "Unknown") for m in meals[:8]]
        listing = "\n".join(f"  - {n}" for n in names)
        return f"Here are some recipes I found:\n{listing}\n\nAsk me about any of these by name for full details!"

    # Full recipe result — format up to 2
    results = []
    for meal in meals[:2]:
        results.append(_format_meal_data(meal))

    return "\n\n---\n\n".join(results)


def handle_recipe_query(user_message: str) -> str:
    """
    Main entry point for the recipe service.
    Uses the LLM to determine search intent, then queries the API.
    """
    client = get_openai_client()

    # Use the LLM to extract search intent
    extraction = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the recipe search intent from the user message. "
                    "Return ONLY a JSON object with keys: "
                    '"type" (one of: "name", "ingredient", "random"), '
                    '"query" (the search term, or empty string for random). '
                    "Examples: "
                    '{"type": "name", "query": "pasta carbonara"} '
                    '{"type": "ingredient", "query": "chicken"} '
                    '{"type": "random", "query": ""}'
                ),
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )

    try:
        intent = json.loads(extraction.choices[0].message.content.strip())
    except json.JSONDecodeError:
        intent = {"type": "name", "query": user_message}

    search_type = intent.get("type", "name")
    query = intent.get("query", user_message)

    if search_type == "random":
        data = get_random_recipe()
    elif search_type == "ingredient":
        data = search_recipe_by_ingredient(query)
    else:
        data = search_recipe_by_name(query)

    return format_recipe_results(data)