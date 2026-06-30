# Configuration

Configuration means the private settings the tool needs before it can connect.

Most users only need one file: `.env`. This file stays on your machine and should never be committed.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Environment variables are settings the tool reads by name.

This tool uses these settings:
- `WIX_API_BASE_URL`
- `WIX_APP_ID` (required)
- `WIX_APP_SECRET` (required)
- `WIX_INSTANCE_ID` (required)
- `WIX_API_KEY` (required for account-level Sites commands)
- `WIX_ACCOUNT_ID` (required for account-level Sites commands)
- `WIX_ACCESS_TOKEN` (optional; manual token override)
- `WIX_TIMEOUT_S` (optional; default is 30)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.

For normal local use, `.env` is the easiest path.
