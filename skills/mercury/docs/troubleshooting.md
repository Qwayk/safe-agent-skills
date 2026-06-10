# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## API token issues

- If `auth check` fails, confirm your `.env` has:
  - `MERCURY_API_BASE_URL` (prod or sandbox)
  - `MERCURY_API_TOKEN` (starts with `secret-token:` per Mercury docs)
  - `MERCURY_AUTH_SCHEME` (`bearer` or `basic`)
