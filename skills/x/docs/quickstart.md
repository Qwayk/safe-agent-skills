# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
x-api-tool onboarding
```

3) Smoke test

```bash
x-api-tool --env-file .env auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
x-api-tool --output json --version
```

If you want to run without creating a real `.env` yet, you can point at `.env.example` (no secrets):

```bash
x-api-tool --env-file .env.example auth check
```
