# Proof and verification

X proof should answer a simple question: what has actually been checked for users, posts, DMs, lists, spaces, and auth-related work, and what still needs live credentials, permissions, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check account/post proof, DM safeguards, and write-plan evidence before trusting X work.

## Last verified

Date (UTC): 2026-06-11
Verified by: Codex README rebuild and source gate cleanup pass
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

## What can go wrong

- **Invalid token / wrong scopes** → `auth check` is a local config/token presence check; verify by running a live read (e.g., `x-api-tool --output json --live api getUsersMe --auth user`) and inspecting a non-2xx status/error; confirm no writes occurred.
- **Rate limiting** → verify the CLI surfaces a non-secret retry/backoff hint; confirm it does not loop/retry-storm.
- **Pagination surprises** → verify results include paging metadata or clear “next page” hints in JSON/text mode.
- **Write safety drift** → verify write plans disclose no-snapshot status, apply without `--ack-no-snapshot` stops before provider/local writes, and apply with `--ack-no-snapshot` creates a receipt for supported write paths.

## Links

- Sources used: `docs/references.md`
- Coverage source of truth: `docs/api_coverage.md`
