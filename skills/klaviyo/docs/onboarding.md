# Onboarding

This tool connects to Klaviyo from your machine.
Keep `.env` private.

## Setup

1) Run: `klaviyo-safe-agent-cli onboarding`
2) Open `.env` and set:
   - `KLAVIYO_API_BASE_URL=https://a.klaviyo.com`
   - `KLAVIYO_API_KEY=<your private key>`
   - `KLAVIYO_COMPANY_ID=<company id for /client/* operations>` (optional)

## First check

Run:

```bash
klaviyo-safe-agent-cli auth check
```

What to do next:

- If `auth check` says `api_key_present: false`, fill `KLAVIYO_API_KEY` in `.env` and run again.
- If you plan to use `/client/*` endpoints, set `KLAVIYO_COMPANY_ID` in `.env`.
- Keep `.env` local and private. Never paste keys into chat.

## What to ask your AI assistant

Use one safe preview first:

- "Show me my tool plan for getting campaign details."
- "Plan a profile update from this source JSON and do not apply live writes."
