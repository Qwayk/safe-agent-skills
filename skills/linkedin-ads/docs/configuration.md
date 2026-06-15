# Configuration

LinkedIn Ads configuration is the local setup an agent needs before it can review ad accounts, campaigns, creatives, targeting, and reporting. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which LinkedIn Ads values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Use a local env file for normal settings. OS environment values can override it when needed.

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
