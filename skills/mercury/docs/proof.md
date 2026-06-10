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

- Date (UTC): 2026-01-29
- Verified by: agent-orchestrator Worker
- Tool version: 0.1.0
- Provider API version (if applicable): Mercury API v1
- Environment: prod or sandbox (set via `MERCURY_API_BASE_URL`)

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `mercury-api-tool --output json --version`

3) Auth/config check (read-only):
- `mercury-api-tool --output json auth check`

4) One representative read query:
- `mercury-api-tool --output json accounts list`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/accounts_list.json`
- `docs/examples/outputs/transactions_list.json`
- `docs/examples/outputs/export_transactions_dry_run.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong (and how we verify)

- **Invalid API token / wrong environment (prod vs sandbox)** → verify with `auth check` returning `ok=false` and a clear error type; confirm nothing changed in Mercury (GET-only tool).
- **Rate limiting** → verify the CLI surfaces a clear, non-secret error; confirm it does not retry-storm.
- **Pagination surprises** → verify exports/reports cap paging with `--max-pages` and that outputs clearly indicate what was fetched.
- **Local file safety drift** (exports/downloads) → verify local writes require `--apply` (and `--yes` for overwrite), and `--plan-in` refuses if arguments/output path don’t match the reviewed plan.
- **Signed URL leakage (attachments)** → verify signed URLs are redacted from JSON outputs/plans/receipts and from verbose HTTP logs (query strings stripped).

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
