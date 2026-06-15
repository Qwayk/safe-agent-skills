# Configuration

Zendesk configuration is the local setup an agent needs before it can review tickets, users, organizations, groups, and support workflow data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Zendesk values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
