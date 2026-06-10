# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Zendesk configuration:
- `ZENDESK_SUBDOMAIN` (recommended, for example `acme` for `https://acme.zendesk.com`)
- `ZENDESK_BASE_URL` (optional override, for example `https://acme.zendesk.com`)
- `ZENDESK_EMAIL` (required for API token auth)
- `ZENDESK_API_TOKEN` (required for API token auth)
- `ZENDESK_OAUTH_ACCESS_TOKEN` (optional; if set, bearer auth is used)
- `ZENDESK_TIMEOUT_S` (optional; default is 30)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
