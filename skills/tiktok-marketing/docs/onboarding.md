# Onboarding

This tool runs on your computer and uses local TikTok credentials.

1. Create the local env file:
   - Run `tiktok-marketing-api-tool --output json onboarding`
   - Or copy `.env.example` to `.env`
2. Fill these values in `.env`:
   - `TIKTOK_MARKETING_API_BASE_URL=https://business-api.tiktok.com`
   - `TIKTOK_MARKETING_APP_ID`
   - `TIKTOK_MARKETING_APP_SECRET`
   - `TIKTOK_MARKETING_ACCESS_TOKEN`
3. Run the live read-only auth check:

```bash
tiktok-marketing-api-tool --output json auth check
```

4. Discover the API surface:
   - `tiktok-marketing-api-tool --output json api ops list`
   - `tiktok-marketing-api-tool --output json api ops show --op oauth2-advertiser-get`
5. Build a safe first plan:

```bash
tiktok-marketing-api-tool --output json --plan-out plan.json api campaign-get --query-json query.json
```

If auth fails:

- Re-check `TIKTOK_MARKETING_APP_ID` and `TIKTOK_MARKETING_APP_SECRET`
- Store a token file with `auth token set --file token.json` if needed
- Re-check token scope or advertiser permissions

## What to ask your AI agent (examples)

- "Can you set up this tool and tell me what values I need from TikTok?"
- "Can you check if my access settings are valid before I run anything live?"
- "Can you draft a plan for one read-only campaign report I can review first?"
- "Can you explain the next safe step if setup is missing?"
