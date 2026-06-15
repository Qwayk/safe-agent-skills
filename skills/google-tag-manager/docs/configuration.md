# Configuration

Google Tag Manager configuration is the local setup an agent needs before it can inspect accounts, containers, workspaces, tags, triggers, and variables. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Google Tag Manager values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)

## Environment variables

Core:
- `GTM_BASE_URL` (optional; default is `https://tagmanager.googleapis.com/`)
- `GTM_TIMEOUT_S` (optional; default is `30`)
- `GTM_MIN_DELAY_S` (optional; default is `4` seconds; throttles all requests)
- `GTM_READ_RETRIES` (optional; default is `5`; used for read-like requests only)
- `GTM_AUTH_MODE` (`adc` | `oauth_refresh_token` | `service_account_json`)
- `GTM_SCOPES` (optional; comma-separated)

OAuth refresh token mode:
- `GTM_OAUTH_CLIENT_ID`
- `GTM_OAUTH_CLIENT_SECRET`
- `GTM_OAUTH_REFRESH_TOKEN`

Service account mode:
- `GTM_SERVICE_ACCOUNT_JSON_PATH`

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
