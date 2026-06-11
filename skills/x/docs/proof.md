# Proof and verification

Use this page when you want the shortest honest answer to one question: what has really been proved for this X skill so far?

You do not need to run these commands yourself. They are here so you or your agent can audit what ran, what came back, and what still depends on local auth, scopes, or approvals.

Rules:
- Never include secrets.
- Use obvious redactions or placeholders in examples.
- Keep this file short and factual.

## Last verified

Date (UTC): 2026-06-07
Verified by: Codex final practical snapshot repair pass
Tool version: 0.1.0
Provider API version (from pinned OpenAPI snapshot): 2.159
Environment: local tests with mocked provider writes / base URL example: https://api.x.com/2

## Smoke checks

Run inside the tool folder:

1. Create venv and install:
- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`

2. Version check with no `.env` required:
- `x-api-tool --output json --no-provenance --version`

3. Local auth check:
- `x-api-tool --output json --env-file .env --no-provenance auth check`

Optional live read check (requires an OAuth user token):
- `x-api-tool --output json --env-file .env --no-provenance --live auth check`

4. One representative offline read query:
- `x-api-tool --output json --env-file .env.example --no-provenance api ops list`

5. One representative offline write plan:
- `x-api-tool --output json --env-file .env.example --no-provenance --no-artifacts api createPosts --auth none --body-json '{}'`

6. One representative write approval shape:
- `x-api-tool --output json --env-file .env.example --no-provenance --no-artifacts --apply --yes --receipt-out /tmp/x-receipt-should-not-exist.json api createPosts --auth none --body-json '{}'`
- Expected without `--ack-no-snapshot`: `refused=true` and no provider write.
- Expected with `--ack-no-snapshot`: the approved write path runs and the receipt records `before_state.status=no_snapshot_available`.

## Example outputs (redacted)

These files are committed:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/api_ops_list.json`
- `docs/examples/outputs/api_call_plan.json`
- `docs/examples/outputs/dm_bulk_send_plan.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

## What can go wrong (and how we verify)

- **Invalid token / wrong scopes** → `auth check` is a local config/token presence check; verify by running a live read (e.g., `x-api-tool --output json --live api getUsersMe --auth user`) and inspecting a non-2xx status/error; confirm no writes occurred.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify write plans disclose no-snapshot status, apply without `--ack-no-snapshot` stops before provider/local writes, and apply with `--ack-no-snapshot` creates a receipt for supported write paths.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
- Debug history: `docs/engineering_notes.md`
