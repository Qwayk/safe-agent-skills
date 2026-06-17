# Configuration

For Fortnox, configuration is the private local setup the skill reads before it can connect to the right tenant, token store, REST API, and websocket stream. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, websocket URL, timeout, token storage, or service-account behavior.

A good first configuration check is: "Show which Fortnox settings are required, which optional settings are present, and confirm the setup without printing secrets."

## Files

- `.env`: local Fortnox app settings
- `.state/token.json`: default Fortnox token cache
- `.state/oauth_state.json`: local OAuth state saved by `auth login`

If `FORTNOX_TOKEN_FILE` is set, only the token path moves there. The OAuth state file stays at `.state/oauth_state.json`.

## Environment variables

- `FORTNOX_API_BASE_URL`: default `https://api.fortnox.se/3`
- `FORTNOX_WS_URL`: default `wss://ws.fortnox.se/topics-v1`
- `FORTNOX_CLIENT_ID`: required for Fortnox OAuth and service-account flows
- `FORTNOX_CLIENT_SECRET`: required for Fortnox OAuth and service-account flows
- `FORTNOX_REDIRECT_URI`: required for Fortnox authorization-code exchange
- `FORTNOX_OAUTH_SCOPES`: optional space- or comma-separated scopes; default `companyinformation`
- `FORTNOX_OAUTH_AUTHORIZE_URL`: optional override; default official authorize URL
- `FORTNOX_OAUTH_TOKEN_URL`: optional override; default official token URL
- `FORTNOX_OAUTH_REVOKE_URL`: optional override; default official revoke URL
- `FORTNOX_SERVICE_TENANT_ID`: required for service-account client-credentials token fetch
- `FORTNOX_API_TOKEN`: optional direct access-token override for local debugging
- `FORTNOX_REFRESH_TOKEN`: optional refresh-token bootstrap if no token file exists yet
- `FORTNOX_TOKEN_FILE`: optional token-file path override
- `FORTNOX_TIMEOUT_S`: optional request timeout; default `30`

## Override rule

OS environment variables override values from `.env`.
