# Connect your Instantly account

Instantly needs a local API key before an agent can inspect campaigns, leads, sending health, and weak spots.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small campaign or account read before asking for lead, campaign, or sending changes.

## Step 1. Create your local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the required fields:
   - `INSTANTLY_API_BASE_URL=https://api.instantly.ai/api/v2`
   - `INSTANTLY_API_KEY=...`
   - `INSTANTLY_TIMEOUT_S=30` (optional)

## Step 2. Create the Instantly API key

Create an API key in Instantly:

1. Open Instantly settings → Integrations: `https://app.instantly.ai/app/settings/integrations`
2. Click **API Keys** in the left sidebar.
3. Click **Create API Key**.
4. Give it a name and select only the scopes you really need.
5. Click **Create**, then copy the API key. Instantly only shows it once.
6. Paste it into your local `.env` file as `INSTANTLY_API_KEY=<your key>`.

Never paste the API key into chat.

## Step 3. Ask for a safe connection check first

Before any real work, ask your agent to confirm the connection first.

Example:

- "Check that my Instantly skill is connected, then show me my active campaigns and the safest review-first jobs to start with."

## Step 4. Ask for the real job

Good next requests:

- "Pull my campaign analytics for the last 7 days and flag what changed."
- "Review my sending accounts and tell me which warmup or vitals issues need attention."
- "Preview moving these leads into another campaign, but stop before apply."
- "Review my webhooks and show me what looks stale or risky."
- "Do a dry-run reviewed plan first. Only apply after I approve."

## If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Wrong API key or missing scopes
- Network or permission restrictions in the connected account

See [Troubleshooting](troubleshooting.md) for common fixes.
