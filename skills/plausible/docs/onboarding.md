# Connect your Plausible account

Plausible needs a local API key before an agent can inspect sites, traffic, goals, conversions, and privacy-friendly reports.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with one site and a short date range before asking for trends or site changes.

## Step 1. Get a Plausible API key

In your Plausible account settings, create an API key (the exact steps can change).
If you plan to use Sites API commands (creating/updating/deleting sites, goals, guests, custom properties), make sure the key has access to the site; destructive operations may require an owner key.

## Step 2. Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `PLAUSIBLE_BASE_URL` (keep the default unless you’re self-hosting)
- `PLAUSIBLE_SITE_ID` (your site/domain identifier in Plausible)
- `PLAUSIBLE_API_KEY` (your API key)

## Step 3. What to ask your AI agent (examples)

For safety, event writes should be planned first and applied only after your explicit approval.
Some writes also need an extra no-snapshot acknowledgement because they do not have an automatic restore point.

- “Confirm the tool is connected and run a weekly report for the last 7 days.”
- “Validate this Stats query JSON, then run it and export results to a file.”
- “Plan a test event (no write). Apply only after I approve.”
- “List all sites and confirm the site settings (timezone + tracker config).”

## If something fails

Common causes:
- Missing or invalid API key
- Wrong base URL (self-hosted vs cloud)
- Wrong site ID/domain mismatches

See [Troubleshooting](troubleshooting.md) for symptoms and fixes.
