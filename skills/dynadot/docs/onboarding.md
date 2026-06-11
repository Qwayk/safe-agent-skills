# Onboarding (non-technical)

This tool runs on your computer, and connects to a vendor API using an API key/token that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview, the needed approval, and the receipt or exact blocker when changes are requested.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill these fields:
   - `DYNADOT_API_KEY` (required): your Dynadot API key.
   - `DYNADOT_API_BASE_URL` (recommended to keep default): `https://api.dynadot.com/api3.json`
   - `DYNADOT_TIMEOUT_S` (optional): request timeout in seconds (default is fine for most users).

## Step 2: Get the API key/token (tool-specific)

How to get a Dynadot API key (high-level, no secrets):

1) Log in to Dynadot.
2) Go to **Tools → API**.
3) Create (or view) your API key.
4) (Optional but recommended) set an **IP whitelist** if you have a stable IP.
5) Copy the API key and paste it into your `.env` as `DYNADOT_API_KEY=...`.

Important note for domain pushes:
- Dynadot uses a **Push Username** for pushes. This is not always the same as the person’s login username/email.
- Make sure the receiver gives you their **Push Username**.

Important note for transfers between two Dynadot accounts:
- You will need **two** `.env` files (one per Dynadot account).
- You run the transfer workflow using the sender as `--env-file`, and you pass the receiver using `--receiver-env-file`.

Rules:
- Use short numbered steps (no jargon).
- Tell the user exactly what to copy/paste into which `.env` field.
- Never instruct the user to paste secrets into chat.
- If the vendor UI offers multiple key types, explicitly name the one required (example: “Admin API key”, not “Content API key”).

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Apply these metadata updates from a spreadsheet and give me a receipt of what changed.”
- “Do a dry-run preview first. Only apply after I approve.”
- “Do a dry-run preview first and tell me whether a saved before-state, no-snapshot approval, or a true blocker applies.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
