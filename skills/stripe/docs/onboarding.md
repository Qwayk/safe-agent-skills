# Onboarding (non-technical)

This tool runs on your computer and connects to Stripe using an API key you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a safe preview.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill `STRIPE_API_KEY`.

Tip: you can also run `stripe-api-tool onboarding` and it will create `.env` for you if it doesn't exist (it will not fill secrets).

## Step 2: Get your Stripe API key

1) Open Stripe Dashboard.
2) Click **Developers** → **API keys**.
3) Copy a key:
   - Prefer a **restricted key** when possible (starts with `rk_...`).
   - A **secret key** also works (starts with `sk_...`).
4) Paste it into your `.env`:
   - `STRIPE_API_KEY=rk_...` (or `STRIPE_API_KEY=sk_...`)

Notes:
- Stripe has **test** and **live** keys. Use a test key first (it typically contains `_test_`).
- Never paste your key into chat. Only paste it into your local `.env` file.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview. If no saved before-state or provider backup is available for a Stripe write, the agent must say that clearly and ask for explicit no-snapshot approval before apply.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Draft metadata update plans from this spreadsheet and tell me what approval is needed before apply.”
- “Do a dry-run preview first, then ask before any Stripe API write runs.”

## Step 4: Smoke test

1) Local configuration check (no network calls):

- `stripe-api-tool --output json auth check`

2) Optional connectivity check (live read-only call to Stripe):

- `stripe-api-tool --output json api --live get-account`

## Step 5: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Using the wrong key mode (test vs live)
- Network/auth restrictions in the vendor account

The real tool should explain common errors in `docs/troubleshooting.md`.
