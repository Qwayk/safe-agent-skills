# Onboarding (non-technical)

You do not need to be technical to start.

1) Create `.env` from `.env.example`.
2) Fill required values:
   - `BLUESKY_IDENTIFIER=<your handle or DID>`
   - `BLUESKY_APP_PASSWORD=<your app password>`
3) Log in once:

```bash
bluesky-safe-cli auth login
```

4) Check auth:

```bash
bluesky-safe-cli auth check
```

5) Add your first safe call:

```bash
bluesky-safe-cli api app-bsky-actor-get-profile --query-json '{"actor":"your-handle.bsky.app"}'
```

That last command is dry-run by default. It only sends live requests if you add `--live`.

## What to ask your AI agent

- "Show me a dry-run plan first."
- "Use a read query with `--live` and no changes."
- "If this API plan is correct, attempt apply with `--live --apply` and show me the refusal."
- "If a write attempt is refused, confirm no provider HTTP happened and no receipt was written."

If anything fails, use `docs/troubleshooting.md`.
