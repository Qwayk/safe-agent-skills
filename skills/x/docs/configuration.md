# Configuration

X configuration is the local setup an agent needs before it can read posts, users, timelines, search results, and account-accessible social data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which X values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

This template uses a `.env` file for configuration.

## Files

- `.env.example`: copy this to `.env` (do not commit `.env`)
- `.state/token.json`: optional OAuth token storage (gitignored)

By default, `.state/token.json` is stored next to your `--env-file`.

## Environment variables

This template uses these placeholder variables:
- `X_API_BASE_URL`
- `X_API_BEARER_TOKEN` (API key style; optional if you use OAuth)
- `X_API_TIMEOUT_S` (optional; default is 30)

When creating a real tool, rename these to a tool-specific prefix, for example:
- `GOOGLE_ADS_...`
- `MICROSOFT_ADS_...`
- `PINTEREST_...`

## OS environment override

OS environment variables override values from the env file.
Use this for CI or container runs.
