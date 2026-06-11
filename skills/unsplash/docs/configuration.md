# Configuration

This tool loads configuration from a local `.env` file (gitignored).

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/auth.json`: optional local auth storage (gitignored), written via `unsplash-api-tool auth key set`
- `.state/runs/`: local proof artifacts for write-capable commands (gitignored)

By default, `.state/` lives next to your `--env-file` path.

## Environment variables

- `UNSPLASH_API_BASE_URL` (required) — usually `https://api.unsplash.com`
- `UNSPLASH_ACCESS_KEY` (required unless you use `.state/auth.json`)
- `UNSPLASH_TIMEOUT_S` (optional, default 30)

## OS environment override

OS environment variables override values from the env file.

