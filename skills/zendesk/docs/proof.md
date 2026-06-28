# Proof and verification

Zendesk proof should answer a simple question: what has actually been checked for tickets, users, organizations, groups, macros, jobs, and support content, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check inventory validation, auth proof, redacted examples, and no-snapshot write refusals before trusting support changes.

## Last verified

Date (UTC): 2026-06-11
Verified by: update this after the current Zendesk docs pass finishes
Tool version: 0.1.0
Provider API version: See the pinned OpenAPI snapshot `info.version`
Environment: local test suite plus offline and safe-read smoke checks

## Smoke checks

Run inside the tool folder:

1. Create venv and install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2. Version check with no `.env` required:
- `zendesk-api-tool --output json --version`

3. Local auth/config check:
- `zendesk-api-tool --output json --env-file .env auth check`

4. Pinned inventory validation:
- `zendesk-api-tool --output json inventory validate`

5. Representative API read plan:
- `zendesk-api-tool --output json --env-file .env api autocomplete-tags --q-query password-reset`

Optional safe live checks:
- `zendesk-api-tool --output json --env-file .env --live auth check`
- `zendesk-api-tool --output json --env-file .env --live api autocomplete-tags --q-query password-reset`

## Example outputs (redacted)

These files are committed:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong

- **Wrong auth or permissions** -> run `--live auth check` and one representative live read; confirm the tool surfaces the status cleanly and no writes occur.
- **Sensitive-data exposure** -> inspect the returned fields before sharing them anywhere; keep local artifacts private even for reads.
- **Write safety drift** -> verify write plans still disclose the no-snapshot limit before Zendesk HTTP when useful before-state is missing.
- **Stub-only write confusion** -> verify demo writes and jobs write rows still refuse honestly instead of pretending to hit Zendesk.
- **Recovery mismatch** -> verify plans stay explicit about no automatic rollback, no backup promise, and no snapshot promise unless a plan says otherwise.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
