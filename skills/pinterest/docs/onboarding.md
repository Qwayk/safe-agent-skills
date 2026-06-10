# Onboarding (non-technical)

This tool runs on your computer and connects to Pinterest using an access token (and optionally a refresh token) that you store locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with previews, snapshots, and safety refusals when a write would be unsafe.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Choose an auth method

You have two options:

1) A short‑lived access token (fastest for a first test)
2) A refresh-token workflow (recommended for ongoing use)

The exact step-by-step is in `docs/authentication.md`.

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill the values described in `docs/configuration.md`.

## Step 3) What to ask your AI agent (examples)

- “Confirm the tool is connected, then export an audit snapshot of my boards and pins into a folder.”
- “If analytics endpoints fail, re-run the snapshot without analytics and explain what permission is missing.”
- “Plan a pin link cleanup for these pins and show me the preview.”

## If something fails

Common causes:
- Expired access token (short-lived tokens)
- Missing/insufficient scopes (analytics often requires extra permissions)

See `docs/troubleshooting.md` for symptoms and fixes.
