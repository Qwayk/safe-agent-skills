# Onboarding (non-technical)

This tool is set up for local use with Google OAuth.

## Steps

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Add the Google OAuth client secrets path:

```bash
GBP_OAUTH_CLIENT_SECRETS_FILE=/path/to/client-secrets.json
```

3. Run login:

```bash
google-business-profile-safe-cli --output json auth login --console
```

4. Confirm status:

```bash
google-business-profile-safe-cli --output json auth check
```

If status is not ok, follow `google-business-profile-safe-cli auth token set` with a fresh credentials JSON.
