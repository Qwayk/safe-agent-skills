# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says no file token is present, run:
  - `threads-api-tool --output json auth code exchange --code <code>`
  - `threads-api-tool --output json --apply auth code exchange --code <code>`
- If token checks fail, use:
  - `threads-api-tool --output json auth check`
  - `threads-api-tool --output json auth debug-token [--input-token <token>]`
  - `threads-api-tool --output json auth token status`
