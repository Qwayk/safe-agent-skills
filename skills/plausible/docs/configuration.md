# Configuration

Plausible configuration is the local setup an agent needs before it can read sites, traffic reports, goals, referrers, and analytics trends. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Plausible values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
