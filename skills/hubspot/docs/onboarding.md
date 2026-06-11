# Onboarding (non-technical)

This tool uses a HubSpot private app access token as the default path.

Your `.env` file stores secrets on your computer. Never paste `.env` or token values into chat.

## Step 1: Create `.env`

1) Copy `.env.example` to `.env`.
2) Keep `HUBSPOT_API_BASE_URL` as `https://api.hubapi.com` unless you use a custom base URL.
3) Paste your HubSpot token into `HUBSPOT_ACCESS_TOKEN`.

## Step 2: Get a HubSpot private app token (recommended default)

1. In HubSpot, open **Settings → Integrations → Private apps**.
2. Create or open a private app and enable the CRM scopes you need.
3. Copy the generated token.
4. Paste only the token into `.env` under `HUBSPOT_ACCESS_TOKEN`.

## Optional: use an existing OAuth JSON token

If you already have an OAuth token JSON file, you can use it with:

```bash
qwayk-hubspot-safe-agent-cli auth token set --file path/to/token.json
```

## Step 3: Run setup checks

```bash
qwayk-hubspot-safe-agent-cli onboarding
qwayk-hubspot-safe-agent-cli --output json auth check
```

## If the check fails

Most failures are:
- Missing values in `.env`
- Wrong HubSpot scopes
- Account tier or object visibility limits

If errors repeat, use the local troubleshooting section and ask for a clear read of what was missing.

## What to ask your AI agent

- “Run setup first, then check what is available in my HubSpot account.”
- “Find the right records with read-only commands before I approve any write.”
- “Show me a dry-run plan. Do not apply HubSpot writes when no saved snapshot is available.”
