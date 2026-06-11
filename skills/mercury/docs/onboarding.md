# Onboarding (non-technical)

This tool runs on your computer and connects to the Mercury API using an API token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Run `mercury-api-tool onboarding` (recommended), or copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the required fields:
   - `MERCURY_API_BASE_URL=https://api.mercury.com/api/v1` (prod) or `https://api-sandbox.mercury.com/api/v1` (sandbox)
   - `MERCURY_API_TOKEN=secret-token:...` (keep private)
   - `MERCURY_AUTH_SCHEME=bearer` (default; or `basic`)

## Step 2: Get the API key/token (tool-specific)

In your Mercury dashboard, create an API token.

Steps (keep it simple):
1) Open Mercury → Settings.
2) Find the API / Developer section (API tokens).
3) Create a new API token and copy it.
4) Paste it into your local `.env` file as `MERCURY_API_TOKEN=...` (never share it).

If Mercury offers token permissions/scopes:
- Choose **read-only** or the **least privileged** option.

Even if Mercury does not offer read-only tokens:
- This tool still refuses non-GET requests, but the token is still sensitive and must be protected.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before writing any local files.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Export my transactions to a local CSV for bookkeeping, but do a dry-run plan first.”
- “Download invoice PDFs locally (dry-run first, then apply).”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Network/auth restrictions in the Mercury account
- Using the wrong environment base URL (prod vs sandbox)

The real tool should explain common errors in `docs/troubleshooting.md`.
