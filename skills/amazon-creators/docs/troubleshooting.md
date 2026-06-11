# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing or expired, the current source tool cannot create or replace the cache automatically yet.
- `auth token fetch` and `auth token set --file token.json` now produce plans; confirmed apply requires explicit no-snapshot approval before token endpoint use or `.state/token.json` writes when no saved snapshot is available.
- Existing cached tokens can still be used by catalog reads.

## Local helper apply refused

This is expected for onboarding env creation and token-cache helpers.
The safe result is `refused=true`, `before_state.status=no_snapshot_available`, and no `.env` or `.state/token.json` write from the blocked flow.
