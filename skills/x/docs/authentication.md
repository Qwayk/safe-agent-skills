# Authentication

This tool supports two auth styles:

## 1) App-only bearer token (server-to-server)

Some endpoints accept an app-only bearer token.

- Configure in `.env` (gitignored): `X_API_BEARER_TOKEN=...`
- Smoke check (safe): `x-api-tool --output json auth check`

## 2) OAuth2 user token (PKCE)

User-context endpoints (posting, DMs, etc.) require OAuth2.

Auth write helpers plan first. Apply requires `--apply --yes --ack-no-snapshot`, then stores the local token or PKCE state and writes a receipt.

### PKCE flow (no browser automation)

1) Configure in `.env` (gitignored):
- `X_API_OAUTH2_CLIENT_ID=...`
- `X_API_OAUTH2_REDIRECT_URI=...` (must exactly match what you configure in the X Developer Portal)
- `X_API_OAUTH2_SCOPES=users.read tweet.read` (add more scopes as needed)
  - For DMs: add `dm.read dm.write`

Recommended redirect URI for CLIs (loopback):
- `X_API_OAUTH2_REDIRECT_URI=http://127.0.0.1:8080/callback`
  - After authorizing in your browser, you can usually copy the final redirect URL from the address bar and paste it into `auth pkce finish --redirect-url ...` (even if the loopback server isn’t running).

2) Start:
- `x-api-tool --output json auth pkce start`
  - Dry-run emits a plan and does not write `.state/pkce.json`.
  - Approved apply writes `.state/pkce.json`, returns the authorization URL, and does not print the code verifier.

3) Finish (after authorizing and being redirected):
- `x-api-tool --output json auth pkce finish --redirect-url '<paste redirect url here>'`
  - Approved apply exchanges the code, stores `.state/token.json`, and redacts token values from output.

### Manual token import (advanced)

If you already have a token JSON file:

- Store attempt: `x-api-tool auth token set --file token.json`
  - Dry-run emits a plan. Approved apply stores `.state/token.json` and redacts token values from output.
- Check status (never prints token values): `x-api-tool auth token status`

Important:
- Never commit `.state/`.
- Never print tokens in logs.
