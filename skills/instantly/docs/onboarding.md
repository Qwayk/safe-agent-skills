# Onboarding (non-technical)

This tool runs on your computer, and connects to a vendor API using an API key/token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the required fields:
   - `INSTANTLY_API_BASE_URL=https://api.instantly.ai/api/v2`
   - `INSTANTLY_API_KEY=...` (your Instantly API key)
   - `INSTANTLY_TIMEOUT_S=30` (optional)

## Step 2: Get the API key/token (tool-specific)

Create an API key in Instantly:

1) Open Instantly settings → Integrations: `https://app.instantly.ai/app/settings/integrations`
2) Click **API Keys** in the left sidebar.
3) Click **Create API Key**.
4) Give it a name and select scopes you want this tool to use.
5) Click **Create**, then copy the API key (it’s only shown once).
6) Paste it into your local `.env` file:
   - `INSTANTLY_API_KEY=<your key>`

Never paste the API key into chat.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Apply these metadata updates from a spreadsheet and give me a receipt of what changed.”
- “Do a dry-run preview first. Only apply after I approve.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
