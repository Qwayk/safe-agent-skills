# Configuration

This tool uses a local env file for configuration and reads optional overrides from your OS environment.

## Files used by the runtime

- `.env` (or your custom file passed by `--env-file`)
- `.state/token.json` when token is set via `auth token set`

`auth token set` saves token JSON beside your env file.

## Environment variables and defaults

Supported values (with `LINKEDIN_ADS_` prefix):

- `LINKEDIN_ADS_BASE_URL` (default: `https://api.linkedin.com/rest`)
- `LINKEDIN_ADS_ACCESS_TOKEN`  
- `LINKEDIN_ADS_TOKEN`  
- `LINKEDIN_ADS_API_TOKEN`
- `LINKEDIN_ADS_LINKEDIN_VERSION` (default: `202605`)
- `LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION` (default: `2.0.0`)
- `LINKEDIN_ADS_TIMEOUT_S` (default: `30`)

If token env vars are empty, config reads `.state/token.json` and uses `access_token` (or `accessToken`, or `token`) from it.

## OS environment override

OS environment variables override values from the selected env file.

This is useful for CI and container runs.
