# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing, run `auth token set` in dry-run first, then apply with `--apply --yes --ack-no-snapshot` after review.
- `auth pkce start` and `auth pkce finish` also plan first and require the same approval before writing PKCE/token state or calling the token endpoint.
- This is intentional until the tool saves real before-state for local auth files.
