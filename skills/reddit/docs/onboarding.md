# Onboarding

You do not need to paste secrets into chat.

## Step by step

1. Run:

```bash
qwayk-reddit-safe-agent-cli onboarding
```

2. Create or open your Reddit app details.
3. If your use case needs Reddit Data API approval, request it before trying live calls.
4. Fill `.env` with:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET` if your app has one
   - `REDDIT_REDIRECT_URI`
   - `REDDIT_CONTACT_USERNAME`
5. Run:

```bash
qwayk-reddit-safe-agent-cli auth login
```

6. Open the printed URL, approve the app, then run:

```bash
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url 'http://127.0.0.1:8080/callback?...'
```

7. Check the connection:

```bash
qwayk-reddit-safe-agent-cli --live auth check
```

## What to ask your AI agent

- “List the pinned Reddit account operations.”
- “Show my Reddit auth status.”
- “Read my Reddit account profile with a live safe call.”
- “Build a dry-run plan to vote on a post.”
