# Configuration

This tool uses a `.env` file for configuration.

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
This is useful in CI or when running in containers.

## Required headers

- `Authorization: Token token=<CALLRAIL_API_TOKEN>`
- `Request-From: <CALLRAIL_REQUEST_FROM>` (if set)
