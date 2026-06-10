# Onboarding (non-technical)

This tool runs on your computer and connects to the Freepik API using an API key that you store locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with previews, dry-run plans, approved download receipts, or missing-approval refusals.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Get a Freepik API key

In your Freepik account dashboard, find the API section and create an API key (the exact steps can change).

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `FREEPIK_API_BASE_URL` (keep the default unless Freepik support tells you otherwise)
- `FREEPIK_API_KEY` (your API key)

## Step 3) What to ask your AI agent (examples)

These are plain-English requests. The agent should show previews and dry-run plans before any licensed download.

- “Search for 40 recipe photos for ‘X’, exclude AI (best-effort), and give me a shortlist.”
- “Preview the top 10 so I can pick the final IDs.”
- “Prepare download plans only for the IDs I approved and report the safe explicit no-snapshot approval.”
- “Preview a batch job from my spreadsheet; try apply only after I approve, and confirm no file or ledger row was written if the tool refuses.”

## If something fails

Common causes:
- Missing/invalid API key
- Account plan limits (search/download quotas)
- Freepik API changes (fields missing → the tool may refuse downloads for safety)

See `docs/troubleshooting.md` for symptoms and fixes.
