# Configuration

Configuration means the private settings the tool reads before it starts a command. For this Contentsquare skill, configuration is mainly local OAuth credentials, API endpoint selection, project targeting, and timeout settings.

Most users only need one file: `.env`. Put private values in `.env` or the `--env-file` and keep them out of chat and Git.

Configuration does not replace Contentsquare permission. You still need OAuth credentials with access to the API family you want to read or change.

A good first configuration check is: confirm the client id is set, the client secret stays hidden, the project id is present when account-level credentials need it, and the API endpoint is either blank or the exact endpoint Contentsquare gave you.

## Environment variables

Required values:

- `CONTENTSQUARE_CLIENT_ID`
- `CONTENTSQUARE_CLIENT_SECRET`

Optional values:

- `CONTENTSQUARE_AUTH_BASE_URL`, default `https://api.contentsquare.com`
- `CONTENTSQUARE_API_BASE_URL`, only when Contentsquare gives you a fixed API endpoint
- `CONTENTSQUARE_PROJECT_ID`, needed when you use account-level OAuth credentials and want token requests to include the documented `project_id`
- `CONTENTSQUARE_TIMEOUT_S`, default `30`

The OAuth token response can return the API endpoint for the account cloud. Leaving `CONTENTSQUARE_API_BASE_URL` empty lets the CLI use that endpoint.

## Files

- `.env.example`: copy this to `.env` before local setup
- `.env`: private local settings file, never committed
- `.state/runs/`: local run records, plans, receipts, and summaries when commands create them

## Precedence

Command-line flags win over `.env` values for the same setting. For example, `--oauth-project-id` overrides `CONTENTSQUARE_PROJECT_ID` for one command.

OS environment variables can also provide the same values when a host or CI system manages secrets outside `.env`.

## What a good setup looks like

A good first setup has:

- OAuth client id and client secret present locally
- no secret values printed in chat, logs, screenshots, or committed files
- project id set when Contentsquare requires it for account-level credentials
- API base URL left blank unless Contentsquare gave a fixed endpoint
- one safe read confirmed before any reviewed change plan
