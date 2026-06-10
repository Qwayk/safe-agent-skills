# TheMealDB

Install slug: `themealdb`

Use this skill when you want your AI agent to search recipes, ingredients, categories, and meal ideas from TheMealDB without any account setup.

This is a small read-only CLI for the official TheMealDB free V1 public API. It uses the public development key `1` by default, so you can start without any secret.

## For non-technical users: Start here (no coding)

- [What you can do](docs/use_cases.md)
- [Setup and first run](docs/onboarding.md)
- [How safety works](docs/safety_model.md)

Plain-English requests you can give an AI agent:

- “Show me meal categories from TheMealDB.”
- “Find meals with chicken breast.”
- “Look up meal 52772.”
- “Give me one random meal idea.”

## For technical users: Start here (CLI)

- [Quickstart](docs/quickstart.md)
- [Command reference](docs/command_reference.md)
- [API coverage](docs/api_coverage.md)

Small command examples:

If you did not activate the local venv, prefix commands with `.venv/bin/`.

```bash
qwayk-themealdb-safe-agent-cli --version
qwayk-themealdb-safe-agent-cli auth check
qwayk-themealdb-safe-agent-cli search name --name "Arrabiata"
qwayk-themealdb-safe-agent-cli filter category --category Seafood
```

## Tool shape

- Read-only only
- Free V1 public endpoints only
- Named commands only
- No secret needed for the default setup
- Deterministic `--output json`

## Validation

Use the blessed local validation command inside this tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```
