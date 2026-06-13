# Connect your Stripe account

Stripe needs a local API key before an agent can inspect customers, payments, subscriptions, invoices, and account data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small customer, payment, or account read before asking for anything involving live money.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill `STRIPE_API_KEY`.

Tip: you can also run `stripe-api-tool onboarding` and it will create `.env` for you if it doesn't exist (it will not fill secrets).

## Step 2: Get your Stripe API key

1. Open Stripe Dashboard.
2. Click **Developers** → **API keys**.
3. Copy a key:
   - Prefer a **restricted key** when possible (starts with `rk_...`).
   - A **secret key** also works (starts with `sk_...`).
4. Paste it into your `.env`:
   - `STRIPE_API_KEY=rk_...` (or `STRIPE_API_KEY=sk_...`)

Notes:
- Stripe has **test** and **live** keys. Use a test key first (it typically contains `_test_`).
- Never paste your key into chat. Only paste it into your local `.env` file.
- If you only need read or review work, a restricted key is the safest place to start.

## Step 3: What to ask your AI agent (examples)

Ask your agent to start with a read-only check, then show a preview. If no saved before-state or provider backup is available for a Stripe write, the agent must say that clearly and ask for explicit no-snapshot approval before apply.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “List recent customers, subscriptions, invoices, and payouts, then tell me what looks important.”
- “Find the right targets safely, then propose changes for my review.”
- “Draft metadata update plans from this spreadsheet and tell me what approval is needed before apply.”
- “Prepare a refund or payout-related plan, but do not run anything live until I approve it.”
- “Do a dry-run reviewed plan first, then ask before any Stripe API write runs.”

## Step 4: Smoke test

1. Local configuration check (no network calls):

- `stripe-api-tool --output json auth check`

2. Optional connectivity check (live read-only call to Stripe):

- `stripe-api-tool --output json api --live get-account`

## Step 5: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Using the wrong key mode (test vs live)
- Network or permission restrictions in the connected account

See `docs/troubleshooting.md` for common errors and fixes.
