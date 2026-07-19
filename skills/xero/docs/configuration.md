# Local configuration

Most users need `.env` and the protected `.state/` folder beside it. Both are excluded from Git.

## Environment variables

```dotenv
XERO_CLIENT_ID=
XERO_REDIRECT_URI=http://localhost:8765/callback
XERO_STATE_DIR=.state
XERO_TIMEOUT_S=30

XERO_CUSTOM_CLIENT_ID=
XERO_CUSTOM_CLIENT_SECRET=

XERO_APP_STORE_CLIENT_ID=
XERO_APP_STORE_CLIENT_SECRET=
```

`XERO_CLIENT_ID` and `XERO_REDIRECT_URI` are for the recommended PKCE flow. The Custom Connection and App Store fields are optional and remain separate.

OS environment variables override the same names in `.env`. `--env-file path/to/private.env` changes which env file is loaded and where the default state folder lives.

## Protected local files

By default, the tool uses:

- `.state/oauth/token.json` for PKCE tokens
- `.state/oauth/custom-connection-token.json` for Custom Connection tokens
- `.state/oauth/app-store-token.json` for App Store tokens
- `.state/tenant.json` for the selected PKCE tenant
- `.state/custom-tenant.json` for the Custom Connection organisation
- `.state/plans/`, `.state/snapshots/`, `.state/executions/`, and `.state/receipts/` for reviewed writes and one-use execution records

Sensitive state, plans, receipts, and protected provider responses are written with owner-only permissions.

## Output

JSON is the default. In JSON mode, stdout is exactly one JSON object for success or failure. `--verbose` writes safe timing lines to stderr without headers or response bodies.
