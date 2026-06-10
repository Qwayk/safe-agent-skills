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
zendesk-api-tool onboarding
```

3) Smoke test

```bash
zendesk-api-tool auth check
```

4) Confirm pinned API coverage (offline)

```bash
zendesk-api-tool --output json inventory validate
```

5) Run an API operation (plan-only by default)

Pick a command from:
- `docs/official_commands_ticketing_2026-03-05.txt`

Example (plan only; no network):

```bash
zendesk-api-tool --output json --env-file .env api autocomplete-tags --q-query password-reset
```

To actually execute reads, add `--live`.
Writes remain plan-first. Apply attempts require explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available (see `docs/safety_model.md`).

If you want a safe machine-readable version output (no `.env` required):

```bash
zendesk-api-tool --output json --version
```

If you want to preview the CLI without creating a real `.env` yet, you can point at `.env.example`:

```bash
zendesk-api-tool --env-file .env.example auth check
```
