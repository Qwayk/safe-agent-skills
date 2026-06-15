# Configuration

Google Analytics configuration is the local setup an agent needs before it can read properties, reports, traffic sources, and analytics metrics. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Google Analytics values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored; next to your `--env-file`)

## Environment variables

Required (typical):
- `GA4_AUTH_MODE` (`adc` is default)
- `GA4_TIMEOUT_S` (default is `30`)

Optional:
- `GA4_SCOPES` (comma or whitespace separated; default is the union of scopes found in the vendored discovery docs)
- `GA4_ADMIN_BASE_URL` (default derives from the vendored Admin discovery doc)
- `GA4_DATA_BASE_URL` (default derives from the vendored Data discovery doc)

Legacy alias:
- `GA4_API_BASE_URL` (if set and `GA4_ADMIN_BASE_URL` / `GA4_DATA_BASE_URL` are missing, it sets both)

Auth mode: `oauth_refresh_token` (secrets; keep local):
- `GA4_OAUTH_CLIENT_ID`
- `GA4_OAUTH_CLIENT_SECRET`
- `GA4_OAUTH_REFRESH_TOKEN`

Auth mode: `service_account_json` (local file path; keep local):
- `GA4_SERVICE_ACCOUNT_JSON`

## OS environment override

OS environment variables override values from the env file (useful for CI/containers).
