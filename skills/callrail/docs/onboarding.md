# Connect your CallRail account

CallRail needs a local API key before an agent can review calls, companies, forms, trackers, and attribution data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small company or recent-calls read before asking for tracking changes.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Set these values:
   - `CALLRAIL_API_TOKEN` = your CallRail API v3 token
   - `CALLRAIL_API_BASE_URL` = keep the example value `https://api.callrail.com` unless you intentionally point somewhere else
   - `CALLRAIL_DEFAULT_ACCOUNT_ID` = optional default account
   - `CALLRAIL_REQUEST_FROM` = optional header for third-party apps
   - `CALLRAIL_TIMEOUT_S` = optional request timeout in seconds

## Step 2: Get the CallRail API token (tool-specific)

In CallRail:

1. In CallRail, open **Integrations -> API Keys / Data Access**.
2. Click **Create New API v3 Key**.
3. Copy the full key value right away. The full key is shown only once and is hidden after 15 minutes.
4. Paste it into `CALLRAIL_API_TOKEN`.

The key type is often read-only by default. If a write command fails while auth check passes, use a key with write access enabled.

## Step 3: What to ask your AI agent (examples)

Start with read-only checks and dry-runs. Ask for a preview before any write.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely, then show a dry-run plan.”
- “Create these tags in preview mode and then apply only after I approve.”
- “Run a read-only validation first, then show a receipt-style proof for any applied action.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Wrong key type (read-only token used for writes)
- Network or permission restrictions in the connected account
- Write actions not enabled on the active API key

When writes fail, share the exact command, payload, and tool output and check for token permissions first.
