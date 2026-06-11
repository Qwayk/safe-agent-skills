# Configuration

This tool uses a `.env` file for configuration.

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
This is useful in CI or when running in containers.
