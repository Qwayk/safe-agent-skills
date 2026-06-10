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
mercury-api-tool onboarding
```

3) Smoke test

```bash
mercury-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
mercury-api-tool --output json --version
```

If you want to validate flag parsing without creating a real `.env` yet, use `--version` (no `.env` required).
