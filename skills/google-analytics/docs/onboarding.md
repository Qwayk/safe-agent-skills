# Connect your Google Analytics account

Google Analytics needs local credentials before an agent can inspect properties, reports, events, or measurement setup.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a property or small report read and confirm the property is the one you meant.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Pick the auth mode you want to use.

If you want the tool to create the starter file for you, run:

```bash
ga4-api-tool onboarding
```

## Step 2: Pick the Google auth mode that fits you

You can connect in three normal ways:

- `adc` if this machine already signs in through Google Cloud.
- `service_account_json` if you have a Google service account key file.
- `oauth_refresh_token` if you want to use a normal Google user account with a refresh token.

The exact fields for each mode are listed in [Authentication details](authentication.md).

## Step 3: Check access before real work

Ask your agent to start with safe checks like:

- "Check the Google Analytics skill is connected."
- "List the accounts and properties I can access."
- "Show me what is safe to review before we plan any changes."

If you want to run the first checks yourself:

```bash
ga4-api-tool auth check
ga4-api-tool admin v1alpha account-summaries list
```

## Step 4: First requests to give your agent

These are good first requests in plain English:

- "Show me the GA4 accounts and properties I can access."
- "Run a safe report for the last 7 days and explain what stands out."
- "Review this property's audiences, conversions, and custom definitions."
- "Plan the change first and stop before any live GA4 write."

## Step 5: If something fails

The most common setup problems are:

- the wrong auth mode in `.env`
- missing Google permissions for the account or property you want
- a bad service account path or refresh token setup

Use [Troubleshooting](troubleshooting.md) if the first checks fail.
