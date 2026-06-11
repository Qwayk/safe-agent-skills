# Authentication

This tool supports these shipped auth modes:

- `service_account_json` (recommended for own-account use)
- `oauth_refresh_token` (required for client-account use)
- `adc` (Google-hosted environments)

Choose one mode in `GOOGLE_MERCHANT_API_AUTH_MODE`.

## 1) service_account_json

Set:

1) `GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON` to the local service account JSON file path.
2) Run:

```bash
google-merchant-api-tool --output json auth check
```

## 2) oauth_refresh_token

Set:

1) `GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN` with a saved refresh-token JSON file path or inline JSON
2) `GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID`
3) `GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET`
4) optionally store the token file with `auth token set --file token.json` for local token file mode.
5) Run:

```bash
google-merchant-api-tool --output json auth check
```

## 3) adc

Set `GOOGLE_MERCHANT_API_AUTH_MODE=adc` when credentials come from Application Default Credentials.
Then run:

```bash
google-merchant-api-tool --output json auth check
```

Important:
- Never commit `.state/`
- Never print tokens in logs
