# Configuration

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
