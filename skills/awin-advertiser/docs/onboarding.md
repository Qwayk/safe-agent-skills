# Onboarding

This skill uses a local `.env` file.

The shortest path is:

1. Copy `.env.example` to `.env`.
2. Fill in your `AWIN_API_TOKEN` and `AWIN_ADVERTISER_ID`.
3. Run:

```bash
awin-advertiser-safe-cli --output json onboarding
awin-advertiser-safe-cli --output json auth check
```

If `auth check` returns `setup_needed: true`, fix the missing `.env` values and run it again.

## What these fields mean

- `AWIN_API_BASE_URL`: the Awin API host. Most users should keep the default `https://api.awin.com`.
- `AWIN_API_TOKEN`: the token used for normal advertiser reads and writes in this skill.
- `AWIN_ADVERTISER_ID`: the advertiser account ID the tool should query or update.
- `AWIN_API_TIMEOUT_S`: optional timeout in seconds if you want a different network timeout.

Conversion orders use the same `AWIN_API_TOKEN`, but the official endpoint expects it in a different auth header under the hood. You do not need a second secret just to start normal advertiser work here.

## What to ask your agent

- "Help me set up the Awin Advertiser skill and tell me exactly what information I still need."
- "Check whether my Awin token is connected correctly before we review any data."
- "I want to review publisher performance for this advertiser. Start with the safest first step."
- "Prepare a dry-run for a transaction batch validation file and stop before apply."
- "Show me how to upload a product feed safely without making the change yet."
