# Proof pack (publish-ready evidence)

Purpose:
- Make this tool proof-first for future posts/pages (E-E-A-T).
- Capture the minimal evidence a customer can trust: what ran, what came back, what can go wrong, and how we verify.

Note: you do not need to run these commands yourself. They are here so you or your reviewer/agent can audit behavior and prove what happened.

Rules:
- Never include secrets (tokens, client secrets, Authorization headers).
- Use obvious redactions and placeholder values in examples.
- Keep this file short and factual.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: qwayk-zendesk-safe-agent-cli maintainers
- Tool version: 0.1.0
- Provider API version: See pinned OpenAPI snapshot `info.version` (offline).
- Environment: offline/local test suite; live writes intentionally requires explicit no-snapshot approval before Zendesk HTTP

## Smoke checks (copy/paste)

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `zendesk-api-tool --output json --version`

3) Auth/config check (read-only; requires `.env`):
- `zendesk-api-tool --output json --env-file .env auth check`

4) One representative API plan (offline; no network):
- `zendesk-api-tool --output json --env-file .env api <operation> [flags...]`
  - For reads: add `--live` to actually call Zendesk.
  - For writes: default is plan-only; apply requires gates such as `--apply --yes --plan-in` (and deletes require `--ack-irreversible` too), then requires explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available.
  - This tool is plan-first and proof-first: keep plan and missing-approval refusal output separate and review both.
  - Expected recovery contract for writes: no automatic rollback promise and no implied snapshot or backup, and no implied restore action.

Latest full local test result:
- `32` tests passed with `.venv/bin/python -m unittest -q`
- `.venv/bin/python -m zendesk_api_tool --output json inventory validate` passed

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json` (example plan shape for `zendesk-api-tool api ...` in dry-run)
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved apply emits a receipt that records no-snapshot approval)

## What can go wrong (and how we verify)

- **Invalid API key / wrong scopes** -> run `zendesk-api-tool --live auth check` and verify `live.status` is `401`/`403` (and `ok=true`). Confirm no writes occurred.
- **Rate limiting** -> verify the CLI shows a non-secret retry/backoff hint; confirm it does not loop.
- **Pagination surprises** -> verify results include paging metadata or clear "next page" hints in JSON/text mode.
- **Write safety drift** -> verify writes require `--apply` (and `--yes`/`--plan-in` for risky/batch), then require explicit no-snapshot approval before Zendesk HTTP when no saved snapshot is available.
- **Recovery contract** -> verify plans include `automatic_rollback: false`, `backups: []`, `snapshots: []`, and `rollback_plan: null`, and that any restore runs as a separate explicit command.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
