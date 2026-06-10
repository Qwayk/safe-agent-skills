# Configuration

This tool uses a local `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/`: local run artifacts (gitignored)

## Environment variables

Required:
- `DYNADOT_API_KEY`: your Dynadot API key.

Recommended (defaults are fine for most users):
- `DYNADOT_API_BASE_URL`: defaults to `https://api.dynadot.com/api3.json`
- `DYNADOT_TIMEOUT_S`: defaults to `30`

Optional:
- `DYNADOT_API_SANDBOX_BASE_URL`: not used automatically yet; reserved for future `--sandbox` support.

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
