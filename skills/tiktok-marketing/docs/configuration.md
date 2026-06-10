# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

This tool uses these variables:

- `TIKTOK_MARKETING_API_BASE_URL`
- `TIKTOK_MARKETING_APP_ID`
- `TIKTOK_MARKETING_APP_SECRET`
- `TIKTOK_MARKETING_ACCESS_TOKEN` (access-token flow)
- `TIKTOK_MARKETING_TIMEOUT_S`

`TIKTOK_MARKETING_ACCESS_TOKEN` is optional when `.state/token.json` is used.

If you want to test live `auth check`, add app credentials and a token in `.env`.

## OS environment override

OS environment variables override values from the `.env` file.
This is useful in CI and containers.
