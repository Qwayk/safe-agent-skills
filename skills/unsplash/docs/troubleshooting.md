# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Access key

- If `auth check` fails, confirm `UNSPLASH_ACCESS_KEY` is set in your `.env` file.
- If you are using local auth storage, confirm it exists with:
  - `unsplash-api-tool auth key status`
