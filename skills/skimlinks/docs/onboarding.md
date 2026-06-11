# Connect your Skimlinks account

Use this page when you want the shortest safe setup path for Skimlinks work.

This skill runs on your machine and connects to Skimlinks using credentials that you store locally. You do not need to write code, but you do need real Skimlinks access.

Keep this one rule in mind first: your `.env` file contains secrets. Keep it private and never paste it into chat.

## What you need

- Merchant API and Reporting API credentials.
- Your Skimlinks publisher ID.
- Your publisher domain ID for Product Key.
- Separate Product Key credentials if Skimlinks enabled Product Key separately for your account.
- A Link Wrapper ID if you want a default ID for local Link Wrapper builds.

## Step 1) Fill the local `.env` file

In the tool folder:

1. Run `skimlinks-safe-cli onboarding`, or copy `.env.example` to `.env`.
2. Fill `SKIMLINKS_CLIENT_ID`, `SKIMLINKS_CLIENT_SECRET`, and `SKIMLINKS_PUBLISHER_ID`.
3. Fill `SKIMLINKS_PUBLISHER_DOMAIN_ID`.
4. Fill `SKIMLINKS_LINK_WRAPPER_ID` if you want a default Link Wrapper ID.
5. Fill `SKIMLINKS_PRODUCT_CLIENT_ID` and `SKIMLINKS_PRODUCT_CLIENT_SECRET` only if Skimlinks gave you Product Key-specific credentials.

## Step 2) Get the right values from Skimlinks

1. Open Skimlinks Publisher Hub.
2. Go to the Toolbox or developer/API area for your account.
3. Copy the Merchant API and Reporting API client ID and client secret.
4. Copy your publisher ID.
5. Copy your publisher domain ID for Product Key.
6. If Product Key is enabled separately, copy the Product Key-specific credentials too.
7. If you use Link Wrapper, copy the Link Wrapper site ID.

Never paste any client secret into chat. If the agent needs to check setup, ask it to run an auth check locally.

## Step 3) Run the first safe checks

These are the best first commands:

```bash
skimlinks-safe-cli --output json --version
skimlinks-safe-cli --output json auth check
skimlinks-safe-cli --output json auth check --scope product
```

If normal auth passes but Product Key auth fails, that usually means Product Key is not enabled or needs different credentials.

## What to ask your agent next

- "Check whether my Skimlinks credentials work."
- "List merchants that match this brand name."
- "Show the reporting metrics available for link reports."
- "Build a Link Wrapper URL for this merchant page without opening the link."
- "Check whether Product Key credentials are configured before using Product Key."
- "Look up Product Key alternatives for this URL using my publisher domain ID."

## If something fails

The most common causes are:

- missing or incorrect values in `.env`
- Product Key not enabled for the account
- a publisher ID or publisher domain ID from the wrong Skimlinks account
- Skimlinks-side network or auth restrictions

Use [Troubleshooting](troubleshooting.md) if the auth checks or first reads fail.
