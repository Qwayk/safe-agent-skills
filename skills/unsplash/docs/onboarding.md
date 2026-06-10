# Onboarding (non-technical)

This tool runs on your computer and uses the Unsplash API with an **Access Key** (Client‑ID auth).

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with previews, plans, and missing-approval refusals for tracked writes.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Get an Unsplash Access Key

In your Unsplash developer dashboard, create an application and copy the **Access Key** (the exact UI can change).

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `UNSPLASH_API_BASE_URL=https://api.unsplash.com`
- `UNSPLASH_ACCESS_KEY=...`

## Step 3) What to ask your AI agent (examples)

- “Confirm the tool is connected, then find 30 photos for ‘X’ and shortlist the best 10.”
- “Plan downloading these approved photo IDs into a folder (no download until I approve).”
- “Try apply for the approved IDs and show the explicit no-snapshot approval.”

## If something fails

Common causes:
- Missing/invalid access key
- Rate limits

See `docs/troubleshooting.md` for symptoms and fixes.
