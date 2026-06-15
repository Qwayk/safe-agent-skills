# Configuration

Threads configuration is the local setup an agent needs before it can read profiles, posts, replies, and account media the connected app can access. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Threads values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Keep secrets local in `.env`, never in chat or logs.

## Environment variables

- `THREADS_API_BASE_URL` (required): Graph API host, usually `https://graph.threads.net`
- `THREADS_API_VERSION` (optional): API version, default `v1.0`
- `THREADS_API_TOKEN` (optional): OAuth user token string. If empty, token is read from `.state/token.json`.
- `THREADS_APP_ID` (required for OAuth flows): Meta app id.
- `THREADS_APP_SECRET` (required for OAuth flows): App secret.
- `THREADS_REDIRECT_URI` (required for authorization-code flow): OAuth redirect URI.
- `THREADS_DEFAULT_USER_ID` (optional): Default user id for commands where user id is not passed.
- `THREADS_TIMEOUT_S` (optional): request timeout in seconds, default `30`.

## Safe setup

1. Copy `.env.example` to `.env`.
2. Fill real values.
3. Run `threads-api-tool onboarding` and then `threads-api-tool auth check`.

`threads-api-tool` reads `.env` by default and also respects OS environment overrides.
