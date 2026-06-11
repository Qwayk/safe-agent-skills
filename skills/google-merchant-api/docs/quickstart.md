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
google-merchant-api-tool onboarding
```

3) Smoke test

```bash
google-merchant-api-tool auth check
```

If you want a safe machine-readable version output:

```bash
google-merchant-api-tool --output json --version
```

Run `auth check` only after you have created a real `.env` with real credentials.
