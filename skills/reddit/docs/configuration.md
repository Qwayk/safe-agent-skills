# Configuration

This tool uses a local `.env` file next to your work folder.

## Required values

- `REDDIT_CLIENT_ID`
- `REDDIT_REDIRECT_URI`
- `REDDIT_CONTACT_USERNAME`

## Usually needed

- `REDDIT_CLIENT_SECRET`
- `REDDIT_OAUTH_SCOPES`

## Optional values

- `REDDIT_API_BASE_URL`
  - Default: `https://oauth.reddit.com`
- `REDDIT_OAUTH_AUTHORIZE_URL`
  - Default: `https://www.reddit.com/api/v1/authorize`
- `REDDIT_OAUTH_TOKEN_URL`
  - Default: `https://www.reddit.com/api/v1/access_token`
- `REDDIT_TIMEOUT_S`
  - Default: `30`
- `REDDIT_USER_AGENT`
  - If blank, the tool builds one from `REDDIT_CONTACT_USERNAME`
- `REDDIT_ACCESS_TOKEN`
  - Optional override for live reads/writes when you do not want to use `.state/token.json`

## Plan safety

Plan files are bound to live safety settings from your public Reddit setup.
The fingerprint includes:
- base API URL
- authorize URL
- token URL
- redirect URI
- OAuth scopes
- client id
- user-agent

If you change any of these values, plans created earlier will be rejected when used with `--plan-in`.

## Local token storage

OAuth tokens saved by this tool live in:

- `.state/token.json`

For a live command to use a saved token, the file must have one of:
- a future token expiry (`expires_at` or equivalent), or
- a `refresh_token` so the tool can refresh the access token.

Without one of these, live commands fail with a validation error until you run `--live auth exchange-code` (or `--live auth refresh`).

That file is local-only and should stay out of git.
