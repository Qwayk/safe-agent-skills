# Connect your Mercury API token

Use this page when you want the shortest safe setup path for Mercury work.

This skill runs on your machine and uses an API token that you store locally. You do not need to write code, but you do need real Mercury API access.

Keep this one rule in mind first: your `.env` file contains secrets. Keep it private and never paste it into chat.

## What you need

- A Mercury API token.
- The right Mercury base URL for production or sandbox.
- A local place to save files if you plan to export or download anything.

## Step 1) Get the Mercury API token

In Mercury, create or copy the API token you want this skill to use.

If Mercury lets you choose scopes or permissions, choose the most limited option that still supports the reads you need.

Even if Mercury does not offer a read-only token, this skill still refuses non-GET remote requests.

## Step 2) Fill the local `.env` file

In the tool folder:

1. Run `mercury-api-tool onboarding`, or copy `.env.example` to `.env`.
2. Fill in your token.
3. Confirm the base URL is correct:
   - production: `https://api.mercury.com/api/v1`
   - sandbox: `https://api-sandbox.mercury.com/api/v1`
4. Leave `MERCURY_AUTH_SCHEME=bearer` unless your setup really needs `basic`.

## Step 3) Run the first safe checks

These are the best first commands:

```bash
mercury-api-tool --output json --version
mercury-api-tool --output json auth check
mercury-api-tool --output json accounts list
```

If the auth check passes and the account list looks right, the setup is good enough to start real work.

## What to ask your agent next

- "Check the Mercury skill is connected, then list my accounts and balances."
- "Preview a CSV export of this month's transactions for bookkeeping."
- "Find the invoice I need and prepare a PDF download plan."

## If something fails

The most common causes are:

- a missing or invalid token
- the wrong base URL
- Mercury-side network or account restrictions

Use [Troubleshooting](troubleshooting.md) if the auth check or first account read fails.
