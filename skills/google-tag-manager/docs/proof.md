# Proof pack (publish-ready evidence)

Purpose:
- show what happened, what it changed, and what was verified
- keep claims small and close to real tool output

Rules:
- never include secrets
- use placeholders in examples
- keep this file short and factual

Use the recovery fields in plan and receipt as part of proof:
- `recovery.end_state`
- `recovery.strategy`
- `recovery.rollback_plan`
- `recovery.rollback_ready`

For supported write families, dry-run plans and apply receipts also include `before_state`:
- `before_state.attempted` (true/false)
- `before_state.path` (normalized read path, if captured)
- `before_state.status` and `before_state.url` (if successful)
- `before_state.body` (or `before_state.body_text` fallback)
- `before_state.artifact_path` when saved to disk

This tool only shows inverse actions that it can emit from GTM discovery. It does not promise snapshots or generic undo.

## Last verified

- Date (UTC): 2026-03-02
- Verified by: agent (unit tests only)
- Tool version: 0.1.0
- Provider API version: v2
- Environment: no live GTM calls in this PR (plan-only); base URL defaults to `https://tagmanager.googleapis.com/`

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `gtm-api-tool --output json --version`

3) Auth/config check (read-only):
- `gtm-api-tool --output json auth check`

4) One representative read query:
- `gtm-api-tool --output json accounts list`

5) One representative write (dry-run plan only):
- `gtm-api-tool --output json --plan-out plan.json accounts update --path accounts/123 --body-json '{}'`

## Example outputs (redacted)

Committed files:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong (and what to check)

- **Invalid credentials / wrong scopes** - verify `auth check` returns a clear failure.
- **Rate limiting / quota errors** - check `--timeout-s` and retry settings.
- **Pagination surprises** - check paging fields or clear next-page hints.
- **Write safety drift** - verify required flags are used (`--apply`, `--yes`, `--plan-in`, `--ack-irreversible`).
- **Recovery mismatch** - verify `recovery.end_state` is `rollback_by_inverse_action` or `irreversible_and_clearly_labeled`, and `rollback_ready` is correct.

## Links

- Sources used: `docs/references.md`
- Coverage reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
