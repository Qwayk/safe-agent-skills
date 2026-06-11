# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

- If `gsc-api-tool auth check` says credentials are missing, run:
  - `gsc-api-tool auth login`
- Credentials are stored under `.state/gsc_oauth_credentials.json` next to your `--env-file`.
- If OAuth scopes changed, re-run `gsc-api-tool auth login` to refresh local credentials.
