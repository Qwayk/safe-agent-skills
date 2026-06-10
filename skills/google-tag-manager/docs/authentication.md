# Authentication

This tool supports three auth modes:

## 1) ADC (Application Default Credentials)

Recommended for local development when you already have `gcloud` set up.

Env:
- `GTM_AUTH_MODE=adc`
- Optional: `GTM_SCOPES` (comma-separated; defaults to full scope coverage from the pinned discovery snapshot)

## 2) OAuth refresh token (user)

Use this when you want user-based access via a long-lived refresh token.

Env:
- `GTM_AUTH_MODE=oauth_refresh_token`
- `GTM_OAUTH_CLIENT_ID`
- `GTM_OAUTH_CLIENT_SECRET`
- `GTM_OAUTH_REFRESH_TOKEN`
- Optional: `GTM_SCOPES` (comma-separated)

## 3) Service account JSON

Use this when you want server-to-server credentials via a service account key file.

Env:
- `GTM_AUTH_MODE=service_account_json`
- `GTM_SERVICE_ACCOUNT_JSON_PATH`
- Optional: `GTM_SCOPES` (comma-separated)

## Smoke test

This is the read-only sanity check that validates credentials and connectivity:

```bash
gtm-api-tool auth check
```

Notes:
- The tool never prints access tokens, refresh tokens, or client secrets.
- Default scopes are broad (this tool targets “100% API coverage”). If you want least privilege, override with:
  - `GTM_SCOPES=https://www.googleapis.com/auth/tagmanager.readonly`
