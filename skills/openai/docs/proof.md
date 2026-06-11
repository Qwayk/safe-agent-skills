# Proof pack (publish-ready evidence)

Purpose:
- Make this tool “proof-first” for future posts/pages (E‑E‑A‑T).
- Capture the minimal evidence a customer can trust: what ran, what came back, what can go wrong, and how we verify.

Note: you don’t need to run these commands yourself. They exist so you (or your reviewer/agent) can audit behavior and prove what happened.

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Use obvious redactions/placeholder values in examples.
- Keep this file short and factual.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: Codex Wave 3 before-state reset
- Tool version: 0.1.0
- Provider API version (if applicable): OpenAI API (2026-03-17 reference)
- Environment: plan-only / base URL: https://api.openai.com/v1
- Tests: full local suite passed (`39 tests, OK`); docs formatting passed (`1 test, OK`); JSON examples parsed successfully.

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `openai-api-tool --output json --version`

3) Auth/config check (read-only):
- `openai-api-tool --output json auth check`

4) One representative read query:
- `openai-api-tool --output json api ListContainers`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/plan_spend_money.example.json` (spend-money plan with `classification.gates.plan_in/yes/ack_spend_money = true`)
- `docs/examples/receipt.example.json`

## What can go wrong (and how we verify)

- **Invalid API key / wrong scopes** → rerun `openai-api-tool --output json auth check --live` so the tool actually calls `/models` and surfaces `ok=false` plus the error details; the offline-only run simply reports which fields are populated.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify writes require the existing gates, then require explicit no-snapshot approval before OpenAI API key use or HTTP when no saved snapshot is available.
- **Write recovery contract**: write plans include `before_state.status: no_snapshot_available` and `recovery` with `automatic_rollback: false`, empty `backups/snapshots`, and `rollback_plan: null` so no-restore behavior is explicit.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
