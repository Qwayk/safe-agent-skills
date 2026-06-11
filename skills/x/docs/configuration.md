# Configuration

This template uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

This template uses these placeholder variables:
- `X_API_BASE_URL`
- `X_API_BEARER_TOKEN` (API key style; optional if you use OAuth)
- `X_API_TIMEOUT_S` (optional; default is 30)

When creating a real tool, rename these to a tool-specific prefix, for example:
- `GOOGLE_ADS_...`
- `MICROSOFT_ADS_...`
- `PINTEREST_...`

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.

