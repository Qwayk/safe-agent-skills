# Configuration

TikTok Marketing configuration is the local setup an agent needs before it can review advertisers, campaigns, ad groups, ads, reports, and creative data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which TikTok Marketing values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Set these variables:

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
