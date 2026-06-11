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
qwayk-hubspot-safe-agent-cli onboarding
```

3) Smoke test

```bash
qwayk-hubspot-safe-agent-cli auth check
```

If you want a safe machine-readable version output:

```bash
qwayk-hubspot-safe-agent-cli --output json --version
```

If you do not have live credentials yet, portfolio-build checks still work:

```bash
qwayk-hubspot-safe-agent-cli --output json --version
qwayk-hubspot-safe-agent-cli onboarding
```
