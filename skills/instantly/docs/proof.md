# Proof and verification

Instantly proof should answer a simple question: what has actually been checked for campaigns, leads, accounts, inboxes, analytics, and send-related workflows, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check campaign/lead proof and send or bulk-plan evidence before trusting outbound work.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: human merge + local validation (unit tests only; no live Instantly API calls)
- Tool version: 0.6.0
- Provider API version: Instantly API v2
- Environment: plan-only / base URL: https://api.instantly.ai/api/v2
- Validation result: `.venv/bin/python -m unittest -q` passed with 118 tests.

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2) Version (no `.env` required):
- `instantly-api-tool --output json --version`

3) Auth/config check (read-only):
- `instantly-api-tool --output json auth check`

4) One representative read query:
- `instantly-api-tool --output json whoami`

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong

- **Invalid API key / wrong scopes** → verify with `auth check` returning `ok=false` and a clear error type; confirm no writes occurred.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify writes require `--apply` (and `--yes` for risky/batch), destructive/irreversible apply requires `--plan-in` where implemented, supported live writes save `before_state`, unsupported live writes require explicit no-snapshot approval before HTTP, receipts show no rollback plan by design, and supported writes include read-back verification.
- **Secret leaks** → verify secret-bearing outputs (API keys, DFY passwords) are never printed to stdout/stderr and are only stored under `.state/sensitive/` behind an explicit acknowledgement flag.

## Note about this PR

This repo change set is designed to be safe for CI:
- Unit tests fully mock HTTP.
- No live Instantly API calls are made during automated validation.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
