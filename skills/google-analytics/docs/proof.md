# Proof and verification

Google Analytics proof should answer a simple question: what has actually been checked for GA4 properties, reports, audiences, links, and admin settings, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check report/property proof and admin-change plan evidence before trusting analytics setup work.

## Last verified

- Date (UTC): 2026-06-04
- Verified by: Codex + Spark builder review
- Tool version: 0.1.0
- Provider snapshots: vendored GA4 discovery JSON (see `docs/references.md`)
- Environment: local (dry-run plans; explicit no-snapshot approval checks; no live GA4 changes in this repo task)

## Smoke checks

Run inside the tool folder:

1) Create venv + install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e '.[dev]'`

2) Version (no `.env` required):
- `ga4-api-tool --output json --version`

3) Auth/config check (read-only):
- `ga4-api-tool --output json auth check`

4) One representative plan (no network):
- `ga4-api-tool --env-file .env admin v1alpha accounts patch --name accounts/123 --body-json '{}'`

5) One representative apply refusal path (no live provider write in this repo task):
- `python3 -m unittest -q tests/test_write_recovery_contract.py`

2026-06-04 Codex validation: full suite 40 tests OK; docs formatting 1 test OK; version smoke OK; plan/refusal example JSON parsed.

## Example outputs (redacted)

These files are committed (unlike `.state/`):
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; old filename kept)

The committed plan and refusal examples now use a real write-like GA4 command shape and show the explicit before-state blocker.

## What can go wrong

- **Invalid credentials / wrong scopes** → verify with `--apply auth check` returning `ok=false` and a clear error type; confirm no writes occurred.
- **Rate limiting** → verify low-risk reads use bounded retries and never print response bodies (which may contain secrets).
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify write apply requires explicit no-snapshot approval before GA4 HTTP after the required gates and plan drift checks.
- **Recovery wording drift** → verify write plans include `recovery`, `backups: []`, `rollback_plan: null`, and `before_state.supported: false`, and do not imply built-in rollback or snapshots.

## Links

- Sources used: `docs/references.md`
- Coverage main reference: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
