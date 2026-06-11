# Configuration

`bluesky-safe-cli` reads local values from `.env` by default.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: shared local auth/session store (gitignored), one file per `--env-file`

## Core environment variables

- `BLUESKY_IDENTIFIER` (required for primary login)
- `BLUESKY_APP_PASSWORD` (required for primary login)
- `BLUESKY_ACCESS_JWT` (optional direct session token)
- `BLUESKY_REFRESH_JWT` (optional direct refresh token)
- `BLUESKY_ADMIN_TOKEN` (optional admin bearer token)
- `BLUESKY_PDS_URL` (optional, override PDS URL)
- `BLUESKY_ENTRYWAY_URL` (default: `https://bsky.social`)
- `BLUESKY_PUBLIC_API_URL` (default: `https://public.api.bsky.app`)
- `BLUESKY_APPVIEW_URL` (default: `https://api.bsky.app`)
- `BLUESKY_CHAT_URL` (default: `https://api.bsky.chat`)
- `BLUESKY_OZONE_URL` (default: `https://mod.bsky.app`)
- `BLUESKY_RELAY_URL` (default: `https://bsky.network`)
- `BLUESKY_TIMEOUT_S` (default: `30`)

## OS environment override

OS environment variables override values from `.env`.
This is useful in CI and container runs.
