# Quickstart

Want the short non-technical path first? Start with [What you can do](use_cases.md) and [Connect your Google Tag Manager account](onboarding.md).

This page is the CLI path when you already want exact commands.

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
gtm-api-tool onboarding
```

3) Smoke test

```bash
gtm-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
gtm-api-tool --output json --version
```

If you want to run the tool without creating a real `.env` yet, you can point at `.env.example`:

```bash
gtm-api-tool --env-file .env.example auth check
```
