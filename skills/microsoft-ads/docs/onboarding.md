# Onboarding (non-technical)

This tool runs on your computer and connects to the Microsoft Advertising API (Microsoft Ads) v13 using OAuth + a DeveloperToken.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview, the needed approval, and the receipt or exact blocker when changes are requested.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the required fields:
   - `MSADS_ENVIRONMENT=prod` (or `sandbox`)
   - `MSADS_DEVELOPER_TOKEN=...`

Where to get your DeveloperToken:
- Microsoft Advertising requires a DeveloperToken for API access.
- The official docs explain how DeveloperTokens work and where to request one; see `docs/references.md` (look for “Developer token”).

## Step 2: Store your OAuth token JSON (local-only)

You (or your agent) will obtain an OAuth token JSON file via your OAuth process (auth code + refresh token), then store it locally:

```bash
msads-api-tool auth token set --file token.json
```

Tokens are stored under `.state/token.json` next to your `.env` file (gitignored).

Where to get your OAuth token JSON:
- Follow the official Microsoft Ads OAuth flow (auth code + refresh token). See `docs/references.md` (look for “OAuth”).
- This tool does not ask you to paste token values into chat. Keep your token JSON file private.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before any change attempt.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Prepare these metadata updates from a spreadsheet and confirm no write is sent yet.”
- “Do a dry-run preview first, then show me the needed approval and receipt path.”

Tip: live API calls require `--live`. Without it, the tool only produces offline/dry-run plans.

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
