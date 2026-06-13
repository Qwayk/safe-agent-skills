# Connect your Klaviyo account

Klaviyo needs a local API key before an agent can inspect lists, segments, profiles, campaigns, flows, forms, or events.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small list or segment read before asking for marketing-data changes.

## Step 1. Create your local `.env` file

In the tool folder:

1. Run `klaviyo-safe-agent-cli onboarding`.
2. Open `.env` in a text editor.
3. Fill the required fields:
   - `KLAVIYO_API_BASE_URL=https://a.klaviyo.com`
   - `KLAVIYO_API_KEY=...`
   - `KLAVIYO_COMPANY_ID=...` only if you want `/client/*` endpoint work
   - `KLAVIYO_TIMEOUT_S=30` is optional

## Step 2. Create the Klaviyo API key

Create a private Klaviyo API key with the smallest scopes you really need.

Suggested path:

1. Sign in to Klaviyo.
2. Open the Klaviyo settings area for API keys.
3. Create a private API key.
4. Give it only the scopes needed for the job.
5. Copy the key and paste it into your local `.env` file as `KLAVIYO_API_KEY=<your key>`.

If you plan to use `/client/*` endpoints, also add your company ID to `KLAVIYO_COMPANY_ID`.

Never paste the API key into chat.

## Step 3. Ask for a safe connection check first

Before any real work, ask your agent to confirm the connection first.

Example:

- "Check that my Klaviyo skill is connected, then show me the safest audience, profile, and campaign reviews to start with."

## Step 4. Ask for the real job

Good next requests:

- "Show me which lists, segments, or campaigns changed recently."
- "Review one profile and its recent events before I change anything."
- "Preview a bulk suppress or unsubscribe change from this file, but stop before apply."
- "Plan a coupon, template, or catalog update and show me the recovery limits."
- "Use a dry-run first. Only apply after I approve."

## If something fails

The most common issues are:

- Missing or incorrect values in `.env`
- Wrong API key or missing scopes
- Missing `KLAVIYO_COMPANY_ID` for `/client/*` work
- Network or permission restrictions in the Klaviyo account

See [Troubleshooting](troubleshooting.md) for common fixes.
