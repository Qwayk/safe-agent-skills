# Connect your X account

X needs local API credentials and token settings before an agent can inspect account data, mentions, posts, DMs, or safe read options.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a safe account or mentions read before asking for posts, replies, DMs, or auth changes.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill at least:
   - `X_API_BASE_URL=https://api.x.com/2`
   - one auth option to start:
     - app bearer token: `X_API_BEARER_TOKEN=...`
     - OAuth user setup: `X_API_OAUTH2_CLIENT_ID=...` and `X_API_OAUTH2_REDIRECT_URI=...`

## Step 2: Create credentials in the X Developer Portal

Open the X Developer Portal and create (or select) your app/project. You will need one of:

### Option A: App-only bearer token

1. In your app settings, locate the app-only bearer token.
2. Copy it into `.env` as `X_API_BEARER_TOKEN=<paste token here>`.

### Option B: OAuth2 user token (recommended for DMs)

1. In your app settings, enable OAuth 2.0 (Authorization Code with PKCE).
2. Set the callback or redirect URL to match your `.env` exactly.
   - Recommended for CLIs (loopback): `X_API_OAUTH2_REDIRECT_URI=http://127.0.0.1:8080/callback`
   - You can usually copy the full redirect URL from your browser’s address bar after authorization, even if the loopback URL can’t be reached.
3. Copy the OAuth2 client ID into `.env` as `X_API_OAUTH2_CLIENT_ID=<paste client id here>`.
4. Set scopes in `.env` and start minimal:
   - `X_API_OAUTH2_SCOPES=users.read tweet.read`
   - For DMs, include: `dm.read dm.write`

## Step 3: Ask for a safe first check

Good first requests:

- “Confirm the tool is connected, then show me the available X API operations.”
- “Check my account, recent mentions, and the safe read options I can run first.”
- “Plan a DM send to this user ID, but do not send it until I approve.”
- “Plan a bulk DM send from this CSV, and block anything missing consent evidence or an opt-out line.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Missing scopes for user-context endpoints (OAuth2).
- Network/auth restrictions in your X developer account

Extra notes for outreach (DMs):
- DMs require **OAuth user-context auth** (not just the app bearer token).
- Whether you *can* DM someone depends on the **recipient’s DM settings** (and your sender account’s status). Use `x-api-tool --live dm can-send --to-username <name>` to check first.
- “Verified” for DM reach is an X product decision (X Premium + eligibility review). The API does not make an account verified.

See `docs/troubleshooting.md` for common errors and fixes.
