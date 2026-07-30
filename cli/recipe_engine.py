"""
recipe_engine.py
-----------------
Core logic that talks to the Groq API and turns a list of ingredients
(+ optional dietary preference) into a single structured recipe.

This file is intentionally dependency-light so it can be copied into
both the CLI app and the web app without changes.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def get_client() -> Groq:
    """Lazily create the Groq client so importing this module never fails
    just because the API key isn't set yet (useful for web app startup)."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Create a .env file (see .env.example) "
                "or set the environment variable before running."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


SYSTEM_PROMPT = """You are a helpful, no-nonsense home-cooking assistant.

Rules you must follow:
1. Use ONLY the ingredients the user listed. You may also assume basic
   pantry staples are available: salt, pepper, water, and cooking oil.
   Do not introduce any other ingredient the user did not mention.
2. Suggest exactly ONE simple, realistic recipe that can be made right now.
3. Respect the user's dietary preference if one is given.
4. Keep instructions short and beginner-friendly (numbered steps).
5. Respond with STRICT JSON ONLY, no markdown, no commentary, matching
   exactly this schema:

{
  "name": "Recipe name",
  "emoji": "single emoji that represents the dish",
  "servings": "e.g. 1-2 servings",
  "ingredients": ["3 eggs", "1 tbsp butter", "..."],
  "steps": ["Step one.", "Step two.", "..."],
  "notes": "optional short tip, or empty string"
}

If the ingredient list is too limited to make anything reasonable, still
do your best to propose the simplest possible dish (e.g. a snack or
side) using only what was given plus pantry staples, and mention that
limitation briefly in "notes".
"""


def build_user_prompt(ingredients: str, preference: str = "") -> str:
    prompt = f"Ingredients available: {ingredients.strip()}"
    if preference and preference.strip():
        prompt += f"\nDietary preference: {preference.strip()}"
    return prompt


def get_recipe(ingredients: str, preference: str = "") -> dict:
    """
    Makes a SINGLE call to the Groq API and returns a parsed recipe dict:
    { name, emoji, servings, ingredients: [...], steps: [...], notes }

    Raises ValueError if ingredients is empty/blank.
    Raises RuntimeError if the API key is missing or the call fails.
    """
    if not ingredients or not ingredients.strip():
        raise ValueError("No ingredients were provided.")

    client = get_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(ingredients, preference)},
        ],
        temperature=0.7,
        max_tokens=800,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: model occasionally wraps JSON in text/backticks despite
        # instructions -- try to salvage the JSON block.
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise RuntimeError("Model did not return valid JSON. Try again.")
        data = json.loads(raw[start : end + 1])

    # Normalize expected fields so callers can rely on them existing.
    data.setdefault("name", "Recipe")
    data.setdefault("emoji", "🍽️")
    data.setdefault("servings", "")
    data.setdefault("ingredients", [])
    data.setdefault("steps", [])
    data.setdefault("notes", "")

    return data


def format_recipe_text(recipe: dict) -> str:
    """Pretty, terminal-friendly formatting of a recipe dict (used by the CLI)."""
    lines = []
    title = f"{recipe.get('emoji', '🍽️')} {recipe.get('name', 'Recipe')}"
    lines.append(title)
    if recipe.get("servings"):
        lines.append(f"   ({recipe['servings']})")
    lines.append("")

    lines.append("Ingredients:")
    for item in recipe.get("ingredients", []):
        lines.append(f"  - {item}")
    lines.append("")

    lines.append("Steps:")
    for i, step in enumerate(recipe.get("steps", []), start=1):
        lines.append(f"  {i}. {step}")

    if recipe.get("notes"):
        lines.append("")
        lines.append(f"Note: {recipe['notes']}")

    return "\n".join(lines)
