# Configuration

This tool uses a `.env` file so the same settings work across local runs.

This is built for Google Merchant Center, not for API keys.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth refresh token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Use these Merchant settings in `.env`:
- `GOOGLE_MERCHANT_API_BASE_URL`
  Required. This is the Merchant API base URL, for example `https://merchantapi.googleapis.com`.
- `GOOGLE_MERCHANT_API_AUTH_MODE`
  Required. Choose `service_account_json`, `oauth_refresh_token`, or `adc`.
- `GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON`
  Required for `service_account_json` mode.
- `GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN`
  Required for `oauth_refresh_token` mode.
- `GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID`
  Required with OAuth refresh-token mode.
- `GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET`
  Required with OAuth refresh-token mode.
- `GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN_FILE`
  Optional helper path in `oauth_refresh_token` mode.
- `GOOGLE_MERCHANT_API_TOKEN_FILE`
  Optional helper path in `oauth_refresh_token` mode.
- `GOOGLE_MERCHANT_API_OAUTH_TOKEN_URI`
  Optional override for token endpoint.
- `GOOGLE_MERCHANT_API_OAUTH_SCOPES`
  Optional comma list. Default is `https://www.googleapis.com/auth/content`.
- `GOOGLE_MERCHANT_API_TIMEOUT_S`
  Optional timeout seconds. Default is 30.

The base URL key used by the live tool is `GOOGLE_MERCHANT_API_BASE_URL`.

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
