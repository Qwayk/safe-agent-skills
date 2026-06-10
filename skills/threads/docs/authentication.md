# Authentication

This tool uses the official Threads OAuth flow for user access tokens and the official client-credentials flow for app tokens.

## Supported commands

- `threads-api-tool auth authorize-url [--scope <scopes>] [--state <value>]`
- `threads-api-tool auth code exchange --code <auth_code>`
- `threads-api-tool auth token status`
- `threads-api-tool auth token exchange-long [--short-token <token>]`
- `threads-api-tool auth token refresh [--long-token <token>]`
- `threads-api-tool auth app-token generate`
- `threads-api-tool auth debug-token [--input-token <token>]`
- `threads-api-tool auth check`

## Write-gated auth commands

These commands are dry-run by default:
- `auth code exchange`
- `auth token exchange-long`
- `auth token refresh`

Review the planned change first. Current `--apply` attempts return a safety refusal before calling Threads token endpoints or writing `.state/token.json`.

## What each command does

- `authorize-url` builds `https://threads.net/oauth/authorize` from your app settings.
- `code exchange` plans the token write; current `--apply` requires explicit no-snapshot approval before `POST /oauth/access_token` or local token writes.
- `token exchange-long` plans the token write; current `--apply` requires explicit no-snapshot approval before `GET /access_token?grant_type=th_exchange_token` or local token writes.
- `token refresh` plans the token write; current `--apply` requires explicit no-snapshot approval before `GET /refresh_access_token?grant_type=th_refresh_token` or local token writes.
- `app-token generate` sends `GET /oauth/access_token?grant_type=client_credentials`.
- `debug-token` sends `GET /debug_token`.
- `check` runs `GET /me` with the active user token.

## Token sources

The tool uses tokens in this order:
1. `THREADS_API_TOKEN`
2. `.state/token.json` next to the active `--env-file`

## Safety notes

- Token values are redacted in normal output, logs, plans, and refusal outputs.
- Never paste real tokens or app secrets in chat.
