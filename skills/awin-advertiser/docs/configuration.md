# Configuration

This tool reads `.env` values and supports OS environment overrides.

## Files

- `.env.example`: copy to `.env` (do not commit `.env`)

## Environment variables

- `AWIN_API_BASE_URL` (optional; default: `https://api.awin.com`)
- `AWIN_API_TOKEN` (required for `auth check`)
- `AWIN_ADVERTISER_ID` (required for `auth check`)
- `AWIN_API_TIMEOUT_S` (optional; default is 30)

## OS environment override

Environment variables override values from the file.
