# Authentication

Google Business Profile authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For locations, reviews, media, attributes, lodging, and business settings, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Google Business Profile credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Authentication notes

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
