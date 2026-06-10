# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)

## Environment variables

- `PLAUSIBLE_BASE_URL` (required) - example: `https://plausible.example.com`
- `PLAUSIBLE_API_KEY` (required) - create an API key in Plausible (used for Stats API v2 and Sites API v1)
- `PLAUSIBLE_SITE_ID` (required) - example: `example.com`
- `PLAUSIBLE_TIMEOUT_S` (optional; default is 30)

## Optional project config (non-secret)

You can also pass `--config <file.json>` for project defaults (paths), for example:
- `reports_out_dir`: default CSV export dir for `report weekly` / `report membership`

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
