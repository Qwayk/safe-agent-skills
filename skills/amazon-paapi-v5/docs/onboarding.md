# Onboarding (non-technical)

This tool runs on your computer and connects to the Amazon Product Advertising API (PA‑API v5) using credentials you store locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent will run the tool for you and report back with results.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1) Get PA‑API credentials (Amazon Associates)

PA‑API access typically requires an Amazon Associates account and API credentials. The exact steps can change by region.

## Step 2) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill the required keys listed in that file.

## Step 3) What to ask your AI agent (examples)

- “Confirm the tool is connected, then search for 20 products for ‘X’ and give me a shortlist with images.”
- “Resolve these Amazon URLs into ASINs and build clean affiliate links.”
- “Run this CSV job and export results to a file.”

## If something fails

Common causes:
- Missing/invalid credentials
- Region/marketplace mismatch
- API access not enabled for the account

See `docs/troubleshooting.md` for symptoms and fixes.

