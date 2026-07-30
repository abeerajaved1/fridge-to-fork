"""
Fridge-to-Fork Recipe Suggester (CLI)
--------------------------------------
Day 2 project - Decoding Bits Training Program

Run:
    python recipe_cli.py

Requires a .env file with GROQ_API_KEY set (see .env.example).
"""

import sys
from recipe_engine import get_recipe, format_recipe_text


def ask_ingredients() -> str:
    ingredients = input("Enter your ingredients: ").strip()
    return ingredients


def ask_preference() -> str:
    preference = input(
        "Any dietary preference? (e.g. vegetarian, no dairy - press Enter to skip): "
    ).strip()
    return preference


def print_recipe(ingredients: str, preference: str) -> bool:
    """Fetches and prints a recipe. Returns True on success, False on failure."""
    print("\nCooking up an idea...\n")
    try:
        recipe = get_recipe(ingredients, preference)
    except ValueError as e:
        print(f"⚠️  {e} Please tell me at least one ingredient.\n")
        return False
    except RuntimeError as e:
        print(f"❌ {e}\n")
        return False
    except Exception as e:
        print(f"❌ Something went wrong talking to Groq: {e}\n")
        return False

    print(format_recipe_text(recipe))
    print()
    return True


def main():
    print("=" * 50)
    print(" 🍳  Fridge-to-Fork Recipe Suggester")
    print("=" * 50)

    # Bonus: ask dietary preference once, up front.
    preference = ask_preference()

    while True:
        ingredients = ask_ingredients()

        if not ingredients:
            print("⚠️  You didn't type anything. Please list at least one ingredient.\n")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == "y":
                continue
            else:
                print("Goodbye! 👋")
                sys.exit(0)

        print_recipe(ingredients, preference)

        # Bonus: let the user ask for another recipe without restarting.
        again = input("Want another recipe? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye! 👋")
            break


if __name__ == "__main__":
    main()
