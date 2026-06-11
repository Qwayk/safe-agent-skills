# Quickstart

If you want the human path first, start with [What you can do with Stripe](use_cases.md), [Connect your Stripe account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is the technical reference for install, setup, and first Stripe commands.

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
stripe-api-tool onboarding
```

3) Smoke test

```bash
stripe-api-tool auth check
```

`auth check` is a local configuration check (no network calls). It verifies that `STRIPE_API_KEY` is present and looks like a Stripe key.

Optional: do a read-only live connectivity check:

```bash
stripe-api-tool api --live get-account
```

If you want a safe machine-readable version output (no `.env` required):

```bash
stripe-api-tool --output json --version
```
