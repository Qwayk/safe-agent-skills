# Onboarding (non-technical)

This tool runs on your computer and connects to Sovrn using local credentials that stay in your own `.env` file.

You do not need to be technical. You can ask an AI agent to run checks, reports, and discovery work for you.

Important:
- This shipped surface is read-only.
- It does not make live changes to your Sovrn account.
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill the Sovrn fields you want to use first.

## Step 2: Get the Sovrn values

You can fill all four values now, or start with only the product area you need first.

### Commerce secret key

1. Log in to the Sovrn Platform.
2. Open Commerce Settings for the site you want to use.
3. Open the key view for that site.
4. If no secret key exists, generate one.
5. Paste it into `SOVRN_COMMERCE_SECRET_KEY`.

### Commerce site API key

1. In the same Commerce site settings area, copy the site API key for that site.
2. Paste it into `SOVRN_COMMERCE_SITE_API_KEY`.

### Advertising reporting API key

1. Log in to the Sovrn Platform.
2. Open `Account` → `API Keys`.
3. Create or copy the Advertising reporting API key.
4. Paste it into `SOVRN_ADVERTISING_API_KEY`.

### Advertising publisher ID

1. Open the Advertising reporting setup area for the same account.
2. Copy the publisher ID that matches your reporting account.
3. Paste it into `SOVRN_ADVERTISING_PUBLISHER_ID`.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests that fit the real shipped surface.

- “Confirm the tool is connected, then show me which Sovrn command bundles are ready.”
- “Check whether these product URLs can be monetized before we use them.”
- “Show me the approved merchants for this campaign.”
- “Pull page and merchant performance for last month.”
- “Compare prices for this product across merchants in one market.”
- “Pull an advertising account report for this publisher.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Mixing the Commerce secret key and the Commerce site API key
- Missing the Advertising publisher ID even though the Advertising API key is present
- Access-gated product APIs in the vendor account

The tool explains common errors in `docs/troubleshooting.md`.
