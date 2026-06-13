# Use TheMealDB with no account

TheMealDB can start with its free public key. You do not need a private secret for normal recipe, ingredient, category, and meal searches.

No secrets are needed for the first run. If the tool creates a local `.env` file, treat it as local setup only; it should not contain a private service token.

Start with a recipe or ingredient search and check a few options before choosing one.

## Step-by-step setup

1. Open this tool folder in your terminal.
2. Create a local virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

If you do not activate the venv, use `.venv/bin/qwayk-themealdb-safe-agent-cli` for the commands below.

3. Create `.env` with the safe defaults:

```bash
qwayk-themealdb-safe-agent-cli onboarding
```

4. Confirm the API is reachable:

```bash
qwayk-themealdb-safe-agent-cli auth check
```

5. Start with a simple read:

```bash
qwayk-themealdb-safe-agent-cli categories
```

## If you want to use your own key

- Put it in `.env` as `THEMEALDB_API_KEY=...`
- Do not paste it into chat
- The tool will redact it from error output

## What to ask your AI agent

These are plain-English examples:

- “Show me the list of meal categories.”
- “Find meals with salmon.”
- “Look up meal 52772.”
- “Show me Canadian meals.”
- “Give me one random meal.”
