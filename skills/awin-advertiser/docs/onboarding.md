# Onboarding

This tool uses a local `.env` file.

1. Copy `.env.example` to `.env`.
2. Fill these fields:
- `AWIN_API_BASE_URL` (default: `https://api.awin.com`)
- `AWIN_API_TOKEN` (API token value)
- `AWIN_ADVERTISER_ID` (numeric or string ID from Awin)
- `AWIN_API_TIMEOUT_S` (optional, seconds)
3. Run:

```bash
awin-advertiser-safe-cli --output json onboarding
awin-advertiser-safe-cli --output json auth check
```

If `auth check` returns `setup_needed: true`, update `.env` and run again.

What these fields mean:
- `AWIN_API_BASE_URL`: the Awin API host. Most users should keep the default.
- `AWIN_API_TOKEN`: the Awin API token for the account doing the work.
- `AWIN_ADVERTISER_ID`: the advertiser account id the tool should query or update.
- `AWIN_API_TIMEOUT_S`: optional timeout in seconds if you want a different network timeout.

What to ask your AI agent (examples):
- “Help me set up this Awin advertiser tool and tell me exactly what information I still need.”
- “Check whether my Awin token is connected correctly before we review any data.”
- “I want to review publisher performance for this advertiser. Start with the safest first step.”
- “Prepare a dry-run for a batch transaction validation file and stop before apply.”
- “Show me how to upload a product feed safely without making the change yet.”
