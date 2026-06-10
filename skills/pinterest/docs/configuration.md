# Configuration

This tool uses a `.env` file for configuration **and secrets**.
Your `.env` is gitignored and should never be committed.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Required for any real API calls:
- Either `PINTEREST_ACCESS_TOKEN` (short-lived)
- Or `PINTEREST_APP_ID` + `PINTEREST_APP_SECRET` + `PINTEREST_REFRESH_TOKEN` (long-term; auto-refresh)

Optional:
- `PINTEREST_API_BASE_URL` (default: `https://api.pinterest.com/v5`)
- `PINTEREST_TIMEOUT_S` (default: `30`)

Example (do not paste real secrets):

```bash
PINTEREST_API_BASE_URL=https://api.pinterest.com/v5
PINTEREST_TIMEOUT_S=30
PINTEREST_APP_ID=1234567
PINTEREST_APP_SECRET=...
PINTEREST_REFRESH_TOKEN=...
```

## Multiple environments

You can use different `.env` files, for example:
- `.env.production`
- `.env.sandbox`

Run with:

```bash
pinterest-api-tool --env-file .env.production auth check
```

Token storage is per env file:
- `.env.production` → `.state/token.json` next to that env file
- `.env.sandbox` → its own `.state/token.json`

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
