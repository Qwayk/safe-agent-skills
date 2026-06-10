# Onboarding (non-technical)

This tool runs on your computer, and connects to the Google Tag Manager API using Google authentication (OAuth / service account / ADC).

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Pick one authentication mode below and fill the matching fields.

## Step 2: Choose an authentication mode

This tool supports three auth modes:

### Option A (recommended for local use): ADC (Application Default Credentials)

1) In your `.env`, set:
   - `GTM_AUTH_MODE=adc`
2) Sign in on your machine (this creates local credentials):
   - Run `gcloud auth application-default login`
3) Make sure the signed-in Google account has access to the GTM account/container you want to manage.

### Option B: OAuth refresh token (user account automation)

1) In Google Cloud Console:
   - Enable the “Google Tag Manager API” on your project.
   - Create an OAuth client (Desktop app or Web app).
2) In your `.env`, set:
   - `GTM_AUTH_MODE=oauth_refresh_token`
   - `GTM_OAUTH_CLIENT_ID=...`
   - `GTM_OAUTH_CLIENT_SECRET=...`
   - `GTM_OAUTH_REFRESH_TOKEN=...`

### Option C: Service account JSON (server-to-server automation)

1) In Google Cloud Console:
   - Enable the “Google Tag Manager API” on your project.
   - Create a service account and download the JSON key file.
2) In your `.env`, set:
   - `GTM_AUTH_MODE=service_account_json`
   - `GTM_SERVICE_ACCOUNT_JSON_PATH=/full/path/to/service-account.json`
3) Ensure this service account is granted access to the GTM account/container (via the GTM UI or your org’s policy).

Notes:
- Default scopes are broad (this tool targets “100% API coverage”). For least-privilege, see `docs/authentication.md`.

## Step 3: Smoke test (safe, read-only)

Run:
- `gtm-api-tool --output json auth check`

If this fails, see `docs/troubleshooting.md`.

## Step 4: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Apply these metadata updates from a spreadsheet and give me a receipt of what changed.”
- “Do a dry-run preview first. Only apply after I approve.”

## Step 5: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- The Google account/service account does not have access to the GTM resources
- The auth mode does not match the `.env` fields you filled

The real tool should explain common errors in `docs/troubleshooting.md`.
