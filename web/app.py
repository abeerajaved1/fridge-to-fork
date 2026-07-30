"""
Fridge-to-Fork Recipe Suggester (Web)
--------------------------------------
Flask app with a small HTML/CSS/JS front end and a single JSON API
endpoint that calls Groq.

Run locally:
    python app.py
Then open http://localhost:5000

Deploy for free: see ../README.md
"""

import os
from flask import Flask, request, jsonify, render_template
from recipe_engine import get_recipe

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/recipe", methods=["POST"])
def api_recipe():
    body = request.get_json(silent=True) or {}
    ingredients = (body.get("ingredients") or "").strip()
    preference = (body.get("preference") or "").strip()

    if not ingredients:
        return jsonify({"error": "Please enter at least one ingredient."}), 400

    try:
        recipe = get_recipe(ingredients, preference)
        return jsonify({"recipe": recipe})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
