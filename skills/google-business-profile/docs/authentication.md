# Authentication

Foundation auth uses Google OAuth installed-app login and local token storage.

## Installed-app flow

1. Put your OAuth client secrets path in `GBP_OAUTH_CLIENT_SECRETS_FILE` (or pass `--client-secrets-file`).
2. Run:

```bash
google-business-profile-safe-cli --output json auth login --console
```

3. The command stores OAuth credentials at `.state/oauth_credentials.json` next to `--env-file`.

## Check/checkpoint

Run:

```bash
google-business-profile-safe-cli --output json auth check
```

This confirms whether valid credentials are present and readable.

## Token helpers

- `google-business-profile-safe-cli auth token set --file token.json`
- `google-business-profile-safe-cli auth token status`
