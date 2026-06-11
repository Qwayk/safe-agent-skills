# Onboarding (non-technical)

This tool runs on your computer and connects to the official PayPal REST API using a PayPal app client ID and client secret that you store locally.

You do not need to be technical. You can ask an AI agent to run the tool for you, and it should report back with a safe preview first for write actions. Current write apply requires explicit no-snapshot approval before PayPal auth or HTTP.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Keep `PAYPAL_ENVIRONMENT=sandbox` while testing.

## Step 2: Get the PayPal app credentials

1. Open the PayPal Developer Dashboard.
2. Go to Apps & Credentials.
3. Under Sandbox, create a new REST app or open an existing one.
4. Copy the client ID into `PAYPAL_CLIENT_ID`.
5. Copy the client secret into `PAYPAL_CLIENT_SECRET`.
6. Leave `PAYPAL_API_BASE_URL` blank unless you have a special PayPal endpoint override.
7. Leave `PAYPAL_PARTNER_ATTRIBUTION_ID` and `PAYPAL_AUTH_ASSERTION` blank unless your PayPal setup needs partner or on-behalf-of headers.

If you already have a production-approved PayPal app, you can switch `PAYPAL_ENVIRONMENT` to `live` later and use the live client ID and secret instead.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview before applying changes.

- “Check the PayPal connection and tell me which API areas are ready.”
- “Show me one order by ID.”
- “List my webhooks and show the details for one webhook.”
- “Prepare a dry-run preview for creating an invoice, then tell me what approval it needs before any live PayPal write.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect client ID / client secret
- Using `live` values while the app is only ready in sandbox
- PayPal account permissions that are required for payouts, partner referrals, referenced payouts, or some dispute flows

Common setup and permission problems are explained in `docs/troubleshooting.md`.
