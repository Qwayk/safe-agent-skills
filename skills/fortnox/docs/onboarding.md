# Connect your Fortnox account

You do not need to learn Fortnox commands first. Once this setup is done, your agent can check company details, customers, suppliers, invoices, bookkeeping records, and other Fortnox data for you.

Keep the setup files private. Do not paste `.env` values, client secrets, access tokens, refresh tokens, OAuth callback URLs with codes, or saved token files into chat.

## Before you start

- You need a Fortnox integration with a client ID, client secret, and redirect URI.
- The local `.env` file is just the private settings file on your computer.
- The redirect URI is the callback address Fortnox sends you back to after approval.

## Step 1: add your private app values

In the skill folder:

1. Run `fortnox-api-tool onboarding`.
2. If `.env` does not exist yet, the command creates a local file for you.
3. Open `.env`.
4. Fill in:
   - `FORTNOX_CLIENT_ID`
   - `FORTNOX_CLIENT_SECRET`
   - `FORTNOX_REDIRECT_URI`

If your host needs a visible sample, use `examples/example.env` as the placeholder guide. If you are setting up the Fortnox app right now, open the Fortnox Developer Portal, create or open your integration, and copy those exact values into `.env`.

## Step 2: ask the agent to start the Fortnox login flow

Run:

```bash
fortnox-api-tool onboarding
fortnox-api-tool auth login
```

Open the returned `authorize_url` in your browser and approve the app for the Fortnox tenant you want to use.

## Step 3: exchange the approval code

After Fortnox redirects back to your callback URL, copy the `code` and `state` values from that URL and run:

```bash
fortnox-api-tool auth exchange-code --code <authorization_code> --state <state>
fortnox-api-tool auth check
```

## Step 4: optional service-account flow

If your Fortnox setup uses the official service-account mode, also save:

- `FORTNOX_SERVICE_TENANT_ID`

Then run:

```bash
fortnox-api-tool auth service-account-token
```

## What success looks like

Setup is complete when `fortnox-api-tool auth check` succeeds and your agent can safely read something simple such as company details, customers, or invoices without asking for more auth values.

## What to ask your AI agent (examples)

- "Set up the Fortnox skill and tell me which values are still missing."
- "Generate the Fortnox login link for me and explain the next step."
- "Exchange this Fortnox approval code and confirm that the account is connected."
- "Check the connection, then show me company details and a few recent invoices."
