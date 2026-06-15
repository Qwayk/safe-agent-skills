# Configuration

CallRail configuration is the local setup an agent needs before it can review calls, forms, companies, trackers, and attribution data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which CallRail values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- The tool stores runtime artifacts under `.state/` when enabled.

## Environment variables

CallRail tool runs with API-key auth only.

- `CALLRAIL_API_BASE_URL` (required; `.env.example` pre-fills `https://api.callrail.com`)
- `CALLRAIL_API_TOKEN` (required)
- `CALLRAIL_REQUEST_FROM` (optional recommendation for third-party integrations)
- `CALLRAIL_DEFAULT_ACCOUNT_ID` (optional default account)
- `CALLRAIL_TIMEOUT_S` (optional; default is 30)

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.

## Required headers

- `Authorization: Token token=<CALLRAIL_API_TOKEN>`
- `Request-From: <CALLRAIL_REQUEST_FROM>` (if set)
