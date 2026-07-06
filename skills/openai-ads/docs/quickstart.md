# Quickstart

Get one useful first result: confirm the tool can read your OpenAI Ads account and list campaigns without changing anything.

## 1. Create local config

Run onboarding:

```bash
openai-ads-safe-agent-cli onboarding
```

Add your Ads Manager API key to `.env`:

```bash
OPENAI_ADS_BASE_URL=https://api.ads.openai.com/v1
OPENAI_ADS_API_KEY=...
OPENAI_ADS_TIMEOUT_S=30
```

## 2. Check the ad account

```bash
openai-ads-safe-agent-cli auth check
```

This reads `GET /ad_account`. It should tell you whether the account can be reached. It does not create, pause, activate, or edit ads.

## 3. See what the tool can help with

```bash
openai-ads-safe-agent-cli api list
```

This lists the Ads API tasks available to your agent, including campaign, ad group, ad, insight, audience, conversion, targeting, and file work.

## 4. Try one read

```bash
openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
```

This asks the Ads API for a small campaign list. It is a read-only check.

## 5. Prepare a change without sending it

```bash
openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

This creates `plan.json`. Review it before asking the agent to do anything live. A real change needs the saved plan and your approval.

## A good first agent request

```text
Use the OpenAI Ads tool. Check the account connection, list up to 10 campaigns, and tell me if anything looks paused, missing setup, or unable to serve. Do not make changes.
```
