# Instagram Login Tool Configuration

This tool reads Instagram Login settings from a local `.env` file.

## Files

- `.env.example`: copy this to `.env`
- `.env`: your local settings file; never commit it
- `.state/token.json`: optional token store written by `auth code exchange`, `auth token exchange-long`, and `auth token refresh`

By default, `.state/token.json` lives next to your `--env-file`.

## Environment variables

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `INSTAGRAM_GRAPH_BASE_URL` | No | `https://graph.instagram.com` | Main Graph host for shipped Instagram Login commands |
| `INSTAGRAM_AUTH_API_BASE_URL` | No | `https://api.instagram.com` | Auth code exchange host |
| `INSTAGRAM_AUTH_WEB_BASE_URL` | No | `https://www.instagram.com` | Browser consent host |
| `INSTAGRAM_GRAPH_VERSION` | No | `v25.0` | Default Graph version for versioned calls |
| `INSTAGRAM_APP_ID` | Yes | none | Meta app ID for Instagram Login |
| `INSTAGRAM_APP_SECRET` | Yes | none | Meta app secret |
| `INSTAGRAM_REDIRECT_URI` | Yes | none | Exact redirect URI registered in the Meta app |
| `INSTAGRAM_ACCESS_TOKEN` | No | none | Optional access token override in `.env` |
| `INSTAGRAM_IG_USER_ID` | No | none | Optional default IG User ID for your own account |
| `INSTAGRAM_TIMEOUT_S` | No | `30` | HTTP timeout in seconds |

## Which token wins

The tool resolves the access token in this order:

1. `INSTAGRAM_ACCESS_TOKEN` from the command environment or `.env`
2. `.state/token.json` next to your `--env-file`

If neither exists, read commands that need auth fail with a clean JSON error.

## OS environment override

OS environment variables override values from `.env`.
That is useful for CI or container runs.
