# Authentication

This tool supports three GA4 auth modes (configured via `GA4_AUTH_MODE`):

## 1) `adc` (Application Default Credentials)

- Recommended for developers who already use Google Cloud locally.
- Uses `google-auth` to locate credentials (env vars / gcloud / workload identity).

## 2) `service_account_json`

- Set:
  - `GA4_AUTH_MODE=service_account_json`
  - `GA4_SERVICE_ACCOUNT_JSON=/absolute/path/to/key.json`

## 3) `oauth_refresh_token`

- Set:
  - `GA4_AUTH_MODE=oauth_refresh_token`
  - `GA4_OAUTH_CLIENT_ID=...`
  - `GA4_OAUTH_CLIENT_SECRET=...`
  - `GA4_OAUTH_REFRESH_TOKEN=...`

### Token helper (optional; local-only)

If you prefer to keep the refresh-token fields in `.state/token.json` (next to your `--env-file`), you can store it with:

```bash
ga4-api-tool auth token set --file token.json
```

Then check status (safe; never prints token values):

```bash
ga4-api-tool auth token status
```

Important:
- Never commit `.state/`
- Never print tokens, refresh tokens, or client secrets in logs
