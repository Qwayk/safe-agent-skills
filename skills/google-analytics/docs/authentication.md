# Authentication

Google Analytics authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For GA4 properties, reports, audiences, links, and admin settings, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Google Analytics credential path is configured, run the safe auth check, and stop before any token write or live account change."

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
