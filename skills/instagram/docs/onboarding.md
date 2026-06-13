# Connect your Instagram account

Instagram needs local app credentials and access tokens for a professional account before an agent can inspect media, comments, mentions, or insights.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start by confirming which Instagram professional account the token reaches.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill these fields:

```text
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
INSTAGRAM_REDIRECT_URI=
```

If you want the tool to create the starter file for you, run:

```bash
instagram-api-tool onboarding
```

## Step 2: Build the Instagram Login URL

Run:

```bash
instagram-api-tool auth login-url --scope instagram_business_basic
```

Add more scopes only when you need them, such as comments, publishing, messages, or insights.

## Step 3: Sign in and exchange the code

Open the login URL in a browser, sign in to the Instagram professional account, approve the requested scopes, then copy the `code` value from the redirect URL.

To finish token exchange or save token state, the tool will plan first and can require explicit no-snapshot approval if it cannot save useful old token state.

The normal exchange command is:

```bash
instagram-api-tool auth code exchange --code YOUR_CODE
```

That first run can show the plan first.
If the tool says no saved before-state is available, rerun the reviewed exchange with:

```bash
instagram-api-tool --apply --ack-no-snapshot auth code exchange --code YOUR_CODE
```

If you already have a valid access token, you can also keep it local in `.env` as `INSTAGRAM_ACCESS_TOKEN`.

## Step 4: Check access before real work

Ask your agent to start with safe checks like:

- "Check the Instagram skill is connected."
- "Show which account this token reaches."
- "List my recent media and comments before we plan any changes."

If you want to run the first checks yourself:

```bash
instagram-api-tool auth check
instagram-api-tool users me --fields user_id,username,account_type
```

## Step 5: First requests to give your agent

These are good first requests in plain English:

- "Show which Instagram account this token reaches."
- "List my recent media and comments."
- "Pull insights for these post IDs."
- "Plan the publish or moderation change first and show me the review steps before any live Instagram write."

## Common blockers

- the account is not an Instagram professional account
- the redirect URI in `.env` does not exactly match the app setting
- the token was not exchanged yet, or it expired
- the app does not have the scopes needed for the command family you want
