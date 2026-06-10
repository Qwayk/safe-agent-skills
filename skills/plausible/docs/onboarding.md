# Onboarding (non-technical)

This tool runs on your computer and connects to your Plausible account using an API key that you store locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Get a Plausible API key

In your Plausible account settings, create an API key (the exact steps can change).
If you plan to use Sites API commands (creating/updating/deleting sites, goals, guests, custom properties), make sure the key has access to the site; destructive operations may require an owner key.

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `PLAUSIBLE_BASE_URL` (keep the default unless you’re self-hosting)
- `PLAUSIBLE_SITE_ID` (your site/domain identifier in Plausible)
- `PLAUSIBLE_API_KEY` (your API key)

## Step 3) What to ask your AI agent (examples)

These are plain-English requests. For safety, event writes should always be planned first and only applied after your explicit approval.

- “Confirm the tool is connected and run a weekly report for the last 7 days.”
- “Validate this Stats query JSON, then run it and export results to a file.”
- “Plan a test event (no write). Apply only after I approve.”
- “List all sites and confirm the site settings (timezone + tracker config).”

## If something fails

Common causes:
- Missing/invalid API key
- Wrong base URL (self-hosted vs cloud)
- Wrong site ID/domain mismatches

See `docs/troubleshooting.md` for symptoms and fixes.
