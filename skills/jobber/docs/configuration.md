# Configuration

Jobber configuration is the local setup an agent needs before it can review clients, requests, quotes, jobs, invoices, and field-service records. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Jobber values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Configuration means the private settings the tool reads before it can connect.

Most users only need `.env` in the project folder.

## Files

- `.env` (required)
- `.state/token.json` (optional OAuth token storage)

`.state/token.json` is created locally by `auth token set` and is ignored by version control.

## Environment variables

- `JOBBER_API_BASE_URL` (default: `https://api.getjobber.com`)
- `JOBBER_TIMEOUT_S` (default: `30`)
- `JOBBER_GRAPHQL_VERSION` (default: `2025-04-16`)
- `JOBBER_CLIENT_ID` (OAuth app client ID)
- `JOBBER_CLIENT_SECRET` (OAuth app secret, keep local)
- `JOBBER_REDIRECT_URI` (OAuth redirect URI)
- `JOBBER_API_TOKEN` (optional manual token fallback)

## Environment precedence

- `.env` values are loaded first.
- OS environment variables override `.env` values.

## Notes

- The CLI reads from `.env` automatically using `--env-file` if you pass a custom path.
- OAuth token file values in `.state/token.json` are used first when present.
- Header value `X-JOBBER-GRAPHQL-VERSION` comes from `JOBBER_GRAPHQL_VERSION`.
