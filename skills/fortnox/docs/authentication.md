# Authentication

Fortnox authentication is meant to be local. The skill needs OAuth app values before it can read company details, customers, invoices, supplier bills, payroll, stock, or websocket events, and those values stay in `.env` or local token files on your machine.

Please do not paste secrets, access tokens, refresh tokens, client secrets, or OAuth callback URLs with codes into chat. Ask the agent to run a connection check and report only whether Fortnox is connected.

A good first auth check is: "Confirm Fortnox auth is configured, run the safe connection check, and tell me what is missing without showing any secret values."

## Normal flow

1. Fill `FORTNOX_CLIENT_ID`, `FORTNOX_CLIENT_SECRET`, and `FORTNOX_REDIRECT_URI` in `.env`.
2. Run:

```bash
fortnox-api-tool auth login
```

3. Open the returned `authorize_url` and approve the app.
4. After Fortnox redirects back to your callback URL, run:

```bash
fortnox-api-tool auth exchange-code --code <authorization_code> --state <state>
```

5. Check the result:

```bash
fortnox-api-tool auth check
```

## Refresh token flow

Fortnox refresh-token renewal is part of the supported auth story.

```bash
fortnox-api-tool auth refresh
```

The refreshed token is stored under `.state/token.json` unless `FORTNOX_TOKEN_FILE` overrides the path. The OAuth state file still stays under `.state/oauth_state.json`.

## Service-account flow

Fortnox documents service-account client credentials after prior consent.

1. Start the first consent with:

```bash
fortnox-api-tool auth login --service-account
```

2. Save the tenant id in `.env`:
- `FORTNOX_SERVICE_TENANT_ID=<tenant id>`

3. Fetch a service-account access token:

```bash
fortnox-api-tool auth service-account-token
```

## Manual token import

For controlled local debugging only, you can still import a token JSON file:

```bash
fortnox-api-tool auth token set --file token.json
fortnox-api-tool auth token status
```

Do not treat that manual path as the only supported customer auth story.
