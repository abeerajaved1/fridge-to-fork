# 🍳 Fridge-to-Fork Recipe Suggester

**Decoding Bits Training Program — Day 2**

Tell it what's in your fridge, get back one recipe you can cook right now — with only the ingredients you actually have. Comes in two flavors:

- **`cli/`** — the terminal program from the assignment spec
- **`web/`** — a browser UI (Flask + HTML/CSS/JS) built on the same engine, ready to deploy for free

Both bonuses are implemented: dietary preference is asked up front, and you can request another recipe without restarting.

---

## How it works

1. You type your ingredients (and optionally a dietary preference).
2. One single request is sent to the Groq API (`llama-3.3-70b-versatile` by default) with strict instructions to use *only* what you listed, plus basic pantry staples (salt, pepper, oil, water).
3. The model returns structured JSON, which is rendered as a clean, readable recipe — no walls of text.
4. Empty input is caught before any API call is made.

The core logic lives in `recipe_engine.py` (duplicated identically into `cli/` and `web/` so each folder can be run or deployed completely on its own).

---

## 1. Get a free Groq API key

1. Go to https://console.groq.com/keys
2. Sign up (free) and click **Create API Key**
3. Copy the key — you'll paste it into a `.env` file next

---

## 2. Run the CLI locally

```bash
cd cli
cp .env.example .env
# open .env and paste your real key after GROQ_API_KEY=

pip install -r ../requirements.txt
python recipe_cli.py
```

Example session:

```
==================================================
 🍳  Fridge-to-Fork Recipe Suggester
==================================================
Any dietary preference? (e.g. vegetarian, no dairy - press Enter to skip):
Enter your ingredients: eggs, butter, cheese, onion

Cooking up an idea...

🍳 Cheesy Scrambled Eggs
   (1-2 servings)

Ingredients:
  - 3 eggs
  - 1 tbsp butter
  - 2 tbsp shredded cheese
  - ¼ onion, diced

Steps:
  1. Dice the onion and set aside.
  2. Whisk the eggs.
  3. Melt butter, cook onion 2 min.
  4. Pour in eggs, stir gently.
  5. Top with cheese, serve.

Want another recipe? (y/n):
```

---

## 3. Run the web app locally

```bash
cd web
cp .env.example .env
# paste your real key into .env

pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** — you'll see an order-pad style form. Fill in your ingredients, hit **Send to kitchen**, and the recipe prints out as a torn ticket/receipt below. Use **Tear off another ticket** to ask for a new one without reloading the page.

---

## 4. Deploy it live, for free

The web app is a standard Flask + gunicorn app, so it deploys on any free Python host. Two easy options:

### Option A — Render.com (recommended, stays deployed)

1. Push this whole project to a **GitHub repo**.
2. Go to https://render.com → sign up free → **New +** → **Blueprint**.
3. Connect your repo. Render will detect `render.yaml` at the project root and configure everything automatically (it points at the `web/` folder).
4. When prompted, paste your `GROQ_API_KEY` as an environment variable (do **not** commit your real key to GitHub — `.env` is already git-ignored).
5. Click **Apply**. In a minute or two you'll get a live URL like `https://fridge-to-fork.onrender.com`.

Notes:
- Render's free web service plan spins down after 15 minutes of inactivity and takes a few seconds to wake back up on the next request — totally fine for a demo/project.
- No credit card required for the free tier.

If you'd rather not use the blueprint, you can configure it manually in the Render dashboard:
- **Root directory:** `web`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment variable:** `GROQ_API_KEY` = your key

### Option B — Replit (fastest, zero config)

1. Go to https://replit.com → **Create App** → **Import from GitHub**, pick your repo.
2. Set the run command to `cd web && python app.py` (Replit's Nix/Python template usually auto-installs `requirements.txt`).
3. In Replit's **Secrets** tool (padlock icon), add `GROQ_API_KEY` with your key.
4. Hit **Run** — Replit gives you a public `https://your-repl-name.replit.app` URL immediately while it's running.

Either option is free and gives you a shareable live link.

---

## Project structure

```
fridge-to-fork/
├── cli/
│   ├── recipe_cli.py        # terminal program (the Day 2 deliverable)
│   ├── recipe_engine.py     # Groq call + formatting (shared logic)
│   └── .env.example
├── web/
│   ├── app.py                # Flask routes: "/" (UI) and "/api/recipe" (JSON API)
│   ├── recipe_engine.py      # same engine, copied so this folder deploys standalone
│   ├── templates/index.html  # "order pad" UI
│   ├── static/style.css      # kitchen-ticket / receipt design
│   ├── static/script.js      # calls /api/recipe, renders the receipt
│   ├── requirements.txt
│   ├── Procfile               # for Render/Railway/Heroku-style hosts
│   └── .env.example
├── requirements.txt
├── render.yaml               # one-click Render blueprint
├── .gitignore
└── README.md
```

## Design notes (web UI)

The UI is themed as a diner **order pad → kitchen ticket**: you fill out a two-line pad (ingredients, dietary note), send it "to the kitchen," and the response prints out as a torn receipt with a rubber-stamp emoji — matching the "one ticket in, one recipe out" nature of the tool. Typeset in Space Mono (ticket/typewriter feel) and Work Sans (readable body text) on a warm paper background.

## Constraints followed

- Only `groq` and `python-dotenv` are used for the API call (Flask/gunicorn are only for serving the optional web UI, not part of the core requirement).
- No web scraping, no database, no file I/O of user data.
- Single API call per recipe request — no conversation history is sent or stored.
- Runs fully in the terminal (`cli/`) and, optionally, in the browser (`web/`).
