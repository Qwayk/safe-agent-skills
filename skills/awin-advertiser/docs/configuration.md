# Configuration

Awin Advertiser configuration is the local setup an agent needs before it can review advertiser programs, publishers, transactions, and performance data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Awin Advertiser values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy to `.env` (do not commit `.env`)

## Environment variables

- `AWIN_API_BASE_URL` (optional; default: `https://api.awin.com`)
- `AWIN_API_TOKEN` (required for `auth check`)
- `AWIN_ADVERTISER_ID` (required for `auth check`)
- `AWIN_API_TIMEOUT_S` (optional; default is 30)

## OS environment override

Environment variables override values from the file.
