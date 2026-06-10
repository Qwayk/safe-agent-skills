# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/runs/`: local run artifacts for write-capable commands (gitignored; lives next to your `--env-file`)

## Environment variables

- `INSTANTLY_API_BASE_URL` (optional; default: `https://api.instantly.ai/api/v2`)
- `INSTANTLY_API_KEY` (required; Instantly API key)
- `INSTANTLY_TIMEOUT_S` (optional; default: `30`)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
