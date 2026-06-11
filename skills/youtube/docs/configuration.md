# Configuration

This tool uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored). The current auth write helpers require explicit no-snapshot approval before creating or replacing this file until local saved snapshot support is available.

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

Supported variables:
- `YOUTUBE_API_KEY` (optional; some public read-only calls)
- `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE` (required to plan OAuth login; local file path)
- `YOUTUBE_OAUTH_SCOPES` (optional; default is `https://www.googleapis.com/auth/youtube`)
- `YOUTUBE_API_BASE_URL` (optional; default is `https://www.googleapis.com`)
- `YOUTUBE_TIMEOUT_S` (optional; default is 30)

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.
