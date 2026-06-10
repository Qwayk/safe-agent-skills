# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Auth failures

- If `auth check` fails, confirm `GTM_AUTH_MODE` and the required env vars are present (see `docs/authentication.md`).
- For ADC mode, ensure your local `gcloud` identity has access to GTM.
