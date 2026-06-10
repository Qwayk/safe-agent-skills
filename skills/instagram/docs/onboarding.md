# Instagram Login Tool Onboarding

This tool is for the official Instagram Login product for Instagram professional accounts.

Keep your `.env` private. Never paste app secrets or access tokens into chat.

## Step 1: Create `.env`

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env`.
3. Fill `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`, and `INSTAGRAM_REDIRECT_URI`.

## Step 2: Get the Meta app values

In the Meta App Dashboard:

1. Create or open the Meta app you use for Instagram Platform.
2. Add the Instagram API product with Instagram Login.
3. Copy the app ID into `INSTAGRAM_APP_ID`.
4. Copy the app secret into `INSTAGRAM_APP_SECRET`.
5. Add your exact OAuth redirect URL in the app settings.
6. Copy that same URL into `INSTAGRAM_REDIRECT_URI`.

## Step 3: Connect the Instagram professional account

Run:

```bash
instagram-api-tool auth login-url --scope instagram_business_basic
```

Open the URL in a browser, sign in to the Instagram professional account, approve the requested scopes, then copy the `code` value from the redirect URL.

Auth write helpers create plans. When the tool cannot save useful old token state, apply requires explicit no-snapshot approval before token exchange or local token writes. To use read commands today, you can also add a valid `INSTAGRAM_ACCESS_TOKEN` to `.env` yourself and keep it private.

## Step 4: Check the connection

Run:

```bash
instagram-api-tool auth check
```

## Good first requests for your agent

- "Check the Instagram connection and tell me which account this token reaches."
- "List my recent media and show the fields before we change anything."
- "Do a dry run for publishing this image, then wait for my approval."
- "Show my recent comments and propose safe moderation actions."

## Common blockers

- the account is not an Instagram professional account
- the redirect URI in `.env` does not exactly match the Meta app setting
- the token was not exchanged yet, or it expired
- the app does not have the scopes needed for the command family you want
