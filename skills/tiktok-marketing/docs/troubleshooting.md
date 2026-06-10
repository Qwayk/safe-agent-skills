# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `auth token status` says the token is missing, run:
  - `tiktok-marketing-api-tool --output json auth token set --file token.json`
- If your token expires, refresh it using your OAuth process, then run `token set` again.
