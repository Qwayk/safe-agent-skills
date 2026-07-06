# Onboarding

You need an eligible OpenAI Ads Manager account and an Ads API key from that account.

## Setup

```bash
openai-ads-safe-agent-cli onboarding
```

The command creates `.env` from `.env.example` when `.env` is missing. Fill:

```bash
OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1
OPENAI_ADS_API_KEY=...
OPENAI_ADS_TIMEOUT_S=30
```

For server-side conversion events, also fill:

```bash
OPENAI_ADS_PIXEL_ID=...
OPENAI_ADS_CONVERSIONS_API_KEY=...
OPENAI_ADS_CONVERSIONS_BASE_URL=https://bzr.openai.com/v1
```

## First check

```bash
openai-ads-safe-agent-cli auth check
```

Expected result: a safe `GET /ad_account` response, or a clear auth/access error with no key printed.
