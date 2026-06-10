# Onboarding (non-technical)

This tool runs on your computer and connects to Skimlinks using credentials that you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview + receipt.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill `SKIMLINKS_CLIENT_ID`, `SKIMLINKS_CLIENT_SECRET`, and `SKIMLINKS_PUBLISHER_ID`.
4) Fill `SKIMLINKS_PUBLISHER_DOMAIN_ID`. Product Key requires this value unless you pass it per command.
5) Fill `SKIMLINKS_LINK_WRAPPER_ID` if you want Link Wrapper URLs to use a default ID.
6) Fill `SKIMLINKS_PRODUCT_CLIENT_ID` and `SKIMLINKS_PRODUCT_CLIENT_SECRET` only if Skimlinks gave you separate Product Key credentials.

## Step 2: Get Skimlinks API credentials

1) Open Skimlinks Publisher Hub.
2) Go to the Toolbox or developer/API area for your account.
3) Find the API credentials for Merchant API and Reporting API.
4) Copy the client ID into `SKIMLINKS_CLIENT_ID`.
5) Copy the client secret into `SKIMLINKS_CLIENT_SECRET`.
6) Copy your publisher ID into `SKIMLINKS_PUBLISHER_ID`.
7) Copy your publisher domain ID into `SKIMLINKS_PUBLISHER_DOMAIN_ID`.
8) If Product Key is enabled separately, copy those Product Key credentials into `SKIMLINKS_PRODUCT_CLIENT_ID` and `SKIMLINKS_PRODUCT_CLIENT_SECRET`.
9) If you use Link Wrapper, copy the Link Wrapper site ID into `SKIMLINKS_LINK_WRAPPER_ID`.

Never paste the client secret into chat. If the agent needs to check setup, ask it to run an auth check locally.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check.

- “Check whether my Skimlinks credentials work.”
- “List merchants that match this brand name.”
- “Show the Reporting API metrics available for link reports.”
- “Build a Link Wrapper URL for this merchant page without opening the link.”
- “Check whether Product Key credentials are configured before using Product Key.”
- “Look up Product Key alternatives for this URL using my publisher domain ID.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Product Key not enabled for the account
- A publisher ID or publisher domain ID from the wrong Skimlinks account
- Network/auth restrictions in the Skimlinks account

The troubleshooting page explains common errors in `docs/troubleshooting.md`.
