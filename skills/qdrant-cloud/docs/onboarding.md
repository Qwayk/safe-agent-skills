# Onboarding (non-technical)

This tool runs on your computer, and connects to a vendor API using an API key/token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview, a safe refusal for ordinary writes, or a provider backup/restore receipt when that exact workflow is approved.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the required fields (the real tool must document exactly which ones).

If an API key contains shell-special characters such as `|`, wrap the value in single quotes:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

If you keep the real `.env` outside this tool folder, ask the agent to use `--env-file /full/path/to/.env`.

## Step 2: Get the API key/token (tool-specific)

When you copy this template to build a real tool, replace this section with exact “where to click” UI steps.

Rules:
- Use short numbered steps (no jargon).
- Tell the user exactly what to copy/paste into which `.env` field.
- Never instruct the user to paste secrets into chat.
- If the vendor UI offers multiple key types, explicitly name the one required (example: “Admin API key”, not “Content API key”).

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Prepare these metadata updates from a spreadsheet and tell me what approval they need before any live write.”
- “Do a dry-run preview first. Only apply after I approve.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
