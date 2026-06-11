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
msads-api-tool onboarding
```

3) Smoke test

```bash
msads-api-tool --live auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
msads-api-tool --output json --version
```

If you want to run the template without creating a real `.env` yet, you can point at `.env.example`:

```bash
msads-api-tool --env-file .env.example auth check
```

Note: `--live` is required for any network request. Without it, the tool will only do offline/dry-run planning.
