# Configuration

This tool uses a `.env` file for configuration.

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
This is useful in CI or when running in containers.
