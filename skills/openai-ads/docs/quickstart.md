# Quickstart

Get one safe first result: check that your agent can reach the OpenAI Ads account without changing campaigns, ads, audiences, or measurement.

## 1. Create local config

```bash
openai-ads-safe-agent-cli onboarding
```

Fill `.env` with your Ads Manager API key:

```bash
OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1
OPENAI_ADS_API_KEY=...
OPENAI_ADS_TIMEOUT_S=30
```

## 2. Check the account

```bash
openai-ads-safe-agent-cli auth check
```

This runs `GET /ad_account` and redacts the key. It does not change the account.

## 3. List available commands

```bash
openai-ads-safe-agent-cli api list
```

## 4. Try a safe read

```bash
openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
```

## 5. Prepare a change without applying it

```bash
openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

Review `plan.json`. Nothing is live yet.
