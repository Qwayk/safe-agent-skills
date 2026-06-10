# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

Requires: **Python 3.12+**.

1) Install (minimal)

```bash
python3 --version  # must be 3.12+
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (contributors): install dev extras:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

3) Smoke test

```bash
amazon-pa-api-tool auth check
```

If you want to run without creating a real `.env` yet, you can point at `.env.example`:

```bash
amazon-pa-api-tool --env-file .env.example auth check
```

Optional: include the raw PA-API response in output:

```bash
amazon-pa-api-tool --include-raw product search --query "air fryer" --limit 3
```

If you are not using an editable install, you can run via module:

```bash
PYTHONPATH=src python3 -m amazon_pa_api_tool auth check
```
