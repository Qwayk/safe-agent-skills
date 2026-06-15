# Configuration

YouTube configuration is the local setup an agent needs before it can research channels, video lists, captions, playlists, and metadata plans. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which YouTube values are required, which ones are optional, and confirm the setup without showing secrets."

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
Use this for CI or container runs.
