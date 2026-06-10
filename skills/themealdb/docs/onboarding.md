# Onboarding

You do not need a secret for the default setup. This tool uses TheMealDB free public V1 key `1` unless you choose to override it.

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
