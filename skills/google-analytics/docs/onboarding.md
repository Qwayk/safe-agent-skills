# Onboarding (non-technical)

This tool runs on your computer and connects to Google Analytics (GA4) using local credentials you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with reads, previews, and safe refusals for write-like requests.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Pick an auth mode (`GA4_AUTH_MODE`) and fill the required fields for that mode (see `docs/authentication.md`).

## Step 2: Get credentials (GA4)

Common options:
- `adc`: use Google’s Application Default Credentials (developer-friendly)
- `service_account_json`: use a service account key JSON file
- `oauth_refresh_token`: use an OAuth refresh token (keep it local)

Rules:
- Use short numbered steps (no jargon).
- Tell the user exactly what to copy/paste into which `.env` field.
- Never instruct the user to paste secrets into chat.
- If there are multiple credential types, explicitly name the required one.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before any write-like request.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Create a dry-run plan first, then prove the tool requires explicit no-snapshot approval before GA4 writes.”
- “Do a dry-run preview first. Do not send GA4 writes when no saved snapshot is available.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
