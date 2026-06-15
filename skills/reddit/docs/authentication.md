# Authentication

Reddit authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For posts, comments, mod actions, users, subreddits, and generated API calls, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Reddit credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Normal flow

1. Fill `.env` with `REDDIT_CLIENT_ID`, `REDDIT_REDIRECT_URI`, and `REDDIT_CONTACT_USERNAME`.
2. Run:

```bash
qwayk-reddit-safe-agent-cli auth login
```

3. Open the printed URL in your browser and approve the app.
4. Copy the full redirect URL and run:

```bash
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url 'http://127.0.0.1:8080/callback?...'
```

5. Check the connection:

```bash
qwayk-reddit-safe-agent-cli --live auth check
```

## Refresh a stored token

```bash
qwayk-reddit-safe-agent-cli --live auth refresh
```

## Manual token import

If you already have a Reddit token JSON file:

```bash
qwayk-reddit-safe-agent-cli auth token set --file token.json
qwayk-reddit-safe-agent-cli auth token status
```

## Notes

- Reddit requires OAuth for Data API access.
- Reddit expects a descriptive `User-Agent`.
- Many apps will need explicit Reddit approval before live access works.
- `auth exchange-code` and `auth refresh` both call Reddit, so they require `--live`.
- A stored `.state/token.json` must include a future expiry value (`expires_at`) or a `refresh_token` for live API calls.
