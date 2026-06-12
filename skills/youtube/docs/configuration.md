# Configuration

Use this page when you need the local settings file names and environment variables for the YouTube skill.

The tool uses a `.env` file for private local settings.

## Files

- `examples/example.env`: copy this to `.env` (do not commit `.env`)
- `.env.example`: available in the source checkout as another local env template
- `.state/token.json`: optional OAuth token storage (gitignored). The current auth helpers can inspect this file, but they do not create or replace it automatically today.

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
