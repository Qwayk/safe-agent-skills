# Configuration

Pinterest configuration is the local setup an agent needs before it can review boards, pins, ads, catalogs, and account reporting. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Pinterest values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Use `.env` for local settings and secrets.
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
Use this for CI or container runs.
