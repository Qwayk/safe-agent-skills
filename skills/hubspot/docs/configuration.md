# Configuration

This tool reads settings from `.env` by default.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`).
- `.state/token.json`: optional OAuth token storage (gitignored).

`.state/token.json` is stored next to your `--env-file`.

## Environment variables

- `HUBSPOT_ACCESS_TOKEN` (primary auth token)
- `HUBSPOT_API_TOKEN` (optional compatibility fallback)
- `HUBSPOT_API_BASE_URL` (optional; default is `https://api.hubapi.com`)
- `HUBSPOT_TIMEOUT_S` (optional; default is `30`)

Command-line flags can override `.env`:
- `--env-file` for a custom file
- `--timeout-s` for timeout in seconds
