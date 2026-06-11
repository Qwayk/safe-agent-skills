# Authentication

Pinterest API v5 uses OAuth.

This tool supports two ways to authenticate:

## Option A: 24‑hour access token (good for first test)

In Pinterest Developers → your app → “Generate Access Tokens”, you can generate a short‑lived access token.

Store it in `.env`:

```bash
PINTEREST_ACCESS_TOKEN=PASTE_HERE
```

Pros: simple.
Cons: expires (often ~24 hours).

## Option B: Refresh-token auth (recommended for long-term use)

With refresh-token auth, you keep a refresh token in `.env` and the tool automatically refreshes access tokens for read commands.

Store these in `.env`:
- `PINTEREST_APP_ID`
- `PINTEREST_APP_SECRET`
- `PINTEREST_REFRESH_TOKEN`

### How to get a refresh token

For now, use a manually provisioned refresh token from your Pinterest developer/OAuth setup and store it in `.env`.

Important:
- `auth login`, `auth code exchange`, and `auth token set` are present in the CLI, but they currently require explicit no-snapshot approval before token exchange, `.state/token.json` writes, or `.env` updates.
- Do not run these helpers expecting them to save local token state until before-state support is added for auth setup writes.

1) Add a redirect URI in Pinterest Developers → your app:
- `http://localhost:8765/` (or any localhost port you prefer)

2) The built-in localhost login command currently requires explicit no-snapshot approval before local token writes:

```bash
PYTHONPATH=src python3 -m pinterest_api_tool auth login
```

It will return a safety refusal instead of saving token state.

Manual OAuth notes:

1) In Pinterest Developers → your app:
   - Add a redirect URI: `http://localhost/`
   - Ensure you request the scopes you need (at minimum for this tool: `boards:read`, `pins:read`, `user_accounts:read`)
   - If you plan to edit pin links, add: `pins:write` (and re-authorize to get a new refresh token)
   - If you want analytics, Pinterest may require additional scopes and/or higher app access tier.

2) Open this URL in your browser (replace `YOUR_APP_ID` and adjust scopes if needed):

```
https://www.pinterest.com/oauth/?client_id=YOUR_APP_ID&redirect_uri=http://localhost/&response_type=code&scope=boards:read,pins:read,user_accounts:read&state=anything123
```

3) Click “Give access”.
   - Pinterest redirects you to: `http://localhost/?code=...&state=...`
   - Your browser will likely show “site can’t be reached”. That’s expected.
   - Copy only the `code=...` value from the URL.

4) The CLI exchange command is also currently requires explicit no-snapshot approval before local token writes:

```bash
pinterest-api-tool auth code exchange --code YOUR_CODE --redirect-uri http://localhost/ --continuous-refresh
```

Use your approved manual OAuth process to get `PINTEREST_REFRESH_TOKEN`, then place it in `.env`.

## Optional: store a token JSON file

If you already have a token JSON (example shape in `examples/token.sample.json`), the storage helper currently requires explicit no-snapshot approval before local token writes:

```bash
pinterest-api-tool auth token set --file token.json
pinterest-api-tool auth token status
```

Future token helper writes are expected to store tokens under `.state/token.json` next to your `--env-file` (per environment), but current helper runs refuse first.

Important:
- Never commit `.env` or `.state/`
- Never print tokens/secrets in logs or chat
