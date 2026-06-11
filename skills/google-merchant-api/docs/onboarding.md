# Onboarding

Use this page when you want the shortest safe setup path for Google Merchant Center.

This tool runs locally and needs one Merchant auth mode in `.env`.
Keep your `.env` file, service-account file, and OAuth token files private, and never paste them into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Pick one auth mode:

```text
GOOGLE_MERCHANT_API_AUTH_MODE=service_account_json
```

Use:

- `service_account_json` for own-account access
- `oauth_refresh_token` for client-account access
- `adc` only when you intentionally want Google Application Default Credentials

## Step 2: Fill the fields for your auth mode

Common fields:

```text
GOOGLE_MERCHANT_API_BASE_URL=https://merchantapi.googleapis.com
GOOGLE_MERCHANT_API_GCP_PROJECT_ID=
GOOGLE_MERCHANT_API_MERCHANT_CENTER_ACCOUNT_ID=
```

If you use service-account access, fill:

```text
GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON=
```

If you use OAuth refresh-token access, fill:

```text
GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN=
GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID=
GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET=
GOOGLE_MERCHANT_API_OAUTH_TOKEN_URI=
```

If you want the tool to create the starter file for you, run:

```bash
google-merchant-api-tool onboarding
```

## Step 3: Check setup before real work

Ask your agent to start with safe checks like:

- "Check the Google Merchant Center skill is configured."
- "List the Merchant account paths that are safe to review first."
- "Show me the safest product, issue, or report reads before we plan changes."

If you want to run the first checks yourself:

```bash
google-merchant-api-tool --output json --version
google-merchant-api-tool --output json auth check
google-merchant-api-tool --output json accounts list
```

The first two checks stay local or configuration-only. The third command is a real Merchant read.

## Step 4: First requests to give your agent

These are good first requests in plain English:

- "Review my Merchant accounts or products safely first."
- "Find issue clusters or disapproved products before we edit anything."
- "Prepare the write plan first and show me the approval steps."
- "For any higher-risk or irreversible change, save the plan and make me review it before apply."

## Step 5: If something fails

The most common setup problems are:

- the wrong auth mode is selected
- a service-account or OAuth file path is missing or wrong
- OAuth mode is missing client credentials
- the Merchant account ID or GCP project ID is wrong for this job

Use [Troubleshooting](troubleshooting.md) if the first checks fail.
