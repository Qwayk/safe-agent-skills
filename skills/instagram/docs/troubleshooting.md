# Instagram Login Tool Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Missing token

- If `auth check` says the access token is missing, first run:
  - `instagram-api-tool auth token status`
- Token write helpers create plans. When no useful token state can be saved, apply requires explicit no-snapshot approval before token exchange or local token writes. For reads today, you can also put a valid `INSTAGRAM_ACCESS_TOKEN` in `.env` yourself and keep it private.

## Expired token

- The token refresh helper creates a plan first and requires explicit no-snapshot approval when no useful token state can be saved.
- If your token is expired, you can also prepare a fresh token outside this tool and update `.env` yourself.

## Wrong scopes

- If reads work but comments, messages, publishing, or insights fail, compare the granted scopes against `docs/authentication.md`.
- Do not switch this tool to Facebook Login just to work around a missing Instagram Login scope. First check whether the feature is excluded by product choice in `docs/api_coverage.md`.
