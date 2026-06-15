# Configuration

Google Search Console configuration is the local setup an agent needs before it can check verified sites, search performance, indexing, and URL data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Google Search Console values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/gsc_oauth_credentials.json`: installed-app OAuth credential storage (gitignored)

By default, `.state/` is stored next to your `--env-file`.

## Environment variables

Supported keys:
- `GSC_BASE_URL` (optional; default `https://searchconsole.googleapis.com`)
- `GSC_TIMEOUT_S` (optional; default `30`)
- `GSC_OAUTH_CLIENT_SECRETS_FILE` (recommended; installed-app OAuth client secrets JSON path)
- `GSC_SERVICE_ACCOUNT_FILE` (optional; service account JSON path)
- `GSC_OAUTH_SCOPES` (optional; comma-separated; default is full `webmasters` scope)

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
