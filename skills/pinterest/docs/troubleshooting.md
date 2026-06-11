# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## OAuth tokens

### “Missing token” or “unauthorized”

1) Run:

```bash
pinterest-api-tool auth token status
pinterest-api-tool auth check
```

2) If you are using the 24‑hour token:
- Confirm `PINTEREST_ACCESS_TOKEN` is set in `.env`
- Generate a new token if it expired

3) If you are using refresh-token auth:
- Confirm `.env` contains `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_REFRESH_TOKEN`
- If the refresh token was revoked, use your manual OAuth process to provision a new refresh token. The CLI auth setup helpers currently require explicit no-snapshot approval before token exchange or local token writes.

### “localhost refused to connect” after “Give access”

That is expected if your redirect URI is `http://localhost/` and you don’t have a local server.
The old next step was to exchange the copied code with the CLI, but that helper currently requires explicit no-snapshot approval before local token writes:

```bash
pinterest-api-tool auth code exchange --code YOUR_CODE --continuous-refresh
```

The localhost login helper is also requires explicit no-snapshot approval before local token writes:

```bash
pinterest-api-tool auth login --redirect-uri http://localhost:8765/
```

## Analytics endpoints fail

Some analytics endpoints require specific OAuth scopes and/or app access tier.
If you get authorization errors, start by confirming the token and app have the required permissions.

Quick workaround:

```bash
pinterest-api-tool audit snapshot --out-dir OUT_DIR --skip-analytics
```

## Boards/pins missing (privacy / sections / secret content)

If you see fewer boards than expected, or no boards with sections:
- It may be true (you really have no sectioned boards), or
- Your token may be missing “secret” scopes (example: `boards:read_secret`, `pins:read_secret`)

If you need secret content in the audit, update your Pinterest app scopes, re-authorize, and get a new refresh token.

## Pin link edits fail (403 / missing scope)

Editing pin links requires Pinterest OAuth write scope:
- `pins:write` (and possibly `pins:write_secret` for secret pins)

If `pinterest-api-tool pins links apply ...` fails with authorization errors during a read-only preview:
1) Add the required scopes in Pinterest Developers for your app.
2) Use your manual OAuth process to get a new refresh token.

## Pin link edits fail (restricted feature: pin_edit)

If you see an error like:
- `restricted feature: pin_edit`

It means Pinterest is blocking pin editing for your app access tier (commonly trial/limited access).

Fix:
1) In Pinterest Developers → your app, click **Upgrade access**.
2) Request the access level that enables pin editing.
3) After approval, use your manual OAuth process to generate a new refresh token.
