# Onboarding (non-technical)

This tool runs on your computer and connects to the **X API v2** using credentials you store locally.

You do not need to be technical. You can simply ask an AI agent to do work, and the agent will run the tool for you and report back with a preview, the approval gates for higher-risk writes, and proof after the work runs.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
2) Open `.env` in a text editor.
3) Fill at least:
   - `X_API_BASE_URL=https://api.x.com/2`
   - One auth option (you can do both):
     - App-only bearer: `X_API_BEARER_TOKEN=...`
     - OAuth2 user token (PKCE): `X_API_OAUTH2_CLIENT_ID=...` and `X_API_OAUTH2_REDIRECT_URI=...`

## Step 2: Create credentials in the X Developer Portal

Open the X Developer Portal and create (or select) your app/project. You will need one of:

### Option A: App-only bearer token

1) In your app settings, locate the app-only bearer token.
2) Copy it and paste into `.env` as:
   - `X_API_BEARER_TOKEN=<paste token here>`

### Option B: OAuth2 user token (recommended for DMs)

1) In your app settings, enable OAuth 2.0 (Authorization Code with PKCE).
2) Set the callback/redirect URL to match your `.env` exactly.
   - Recommended for CLIs (loopback): `X_API_OAUTH2_REDIRECT_URI=http://127.0.0.1:8080/callback`
   - You can usually copy the full redirect URL from your browser’s address bar after authorization, even if the loopback URL can’t be reached.
3) Copy the OAuth2 client id into `.env`:
   - `X_API_OAUTH2_CLIENT_ID=<paste client id here>`
4) Set scopes in `.env` (start minimal and add as needed):
   - `X_API_OAUTH2_SCOPES=users.read tweet.read`
   - For DMs, include: `dm.read dm.write`

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only check, then show a preview. Current write attempts should refuse safely before sending, posting, or storing token state.

- “Confirm the tool is connected, then show me the available X API operations.”
- “Plan a DM send to this user id, but don’t send it until I approve.”
- “Plan a bulk DM send from this CSV, and refuse anything missing consent evidence.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Missing scopes for user-context endpoints (OAuth2)
- Network/auth restrictions in your X developer account

Extra notes for outreach (DMs):
- DMs require **OAuth user-context auth** (not just the app bearer token).
- Whether you *can* DM someone depends on the **recipient’s DM settings** (and your sender account’s status). Use `x-api-tool --live dm can-send --to-username <name>` to check first.
- “Verified” for DM reach is an X product decision (X Premium + eligibility review). The API does not make an account verified.

The real tool should explain common errors in `docs/troubleshooting.md`.
