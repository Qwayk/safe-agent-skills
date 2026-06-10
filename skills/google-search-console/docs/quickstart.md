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
gsc-api-tool onboarding
```

3) Smoke test

```bash
gsc-api-tool auth check
```

If you are using installed-app OAuth and this is your first run, do login once:

```bash
gsc-api-tool auth login
gsc-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
gsc-api-tool --output json --version
```

If you want to validate coverage without credentials, run (offline):

```bash
gsc-api-tool --output json operations validate
```
