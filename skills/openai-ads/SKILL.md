---
name: openai-ads
description: Use when the user asks an agent to inspect, plan, report on, or safely change ChatGPT Ads / OpenAI Ads campaigns, ad groups, ads, insights, targeting, product-feed setup, custom audiences, files, conversions, pixels, image tags, or server-side conversion events.
---

# OpenAI Ads

Use this skill when the user asks about ChatGPT Ads or OpenAI Ads work that should go through the official OpenAI Ads API.

This skill is safer than generic API access because the agent must stay inside the `openai-ads-safe-agent-cli` command surface. It can read account and campaign data directly, but live changes require a reviewed plan first. Spend, serving, upload, audience, account, auth, and measurement changes need extra approval. Secrets, pixel IDs where private, audience rows, customer IDs, raw emails, external IDs, and conversion API keys must not be printed.

## Start

First check the available commands:

```bash
openai-ads-safe-agent-cli --output json api list
```

If credentials may not be set up, run:

```bash
openai-ads-safe-agent-cli onboarding
openai-ads-safe-agent-cli auth check
```

## Use The CLI

Use explicit commands only. Do not improvise raw HTTP calls.

Safe read examples:

```bash
openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
openai-ads-safe-agent-cli api targeting get-geo-lookup --query q="San Francisco" --query limit=5
openai-ads-safe-agent-cli measurement events-list
```

Plan-first write example:

```bash
openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

Apply only after the user reviews the saved plan:

```bash
openai-ads-safe-agent-cli --apply --yes --plan-in plan.json --ack-no-snapshot --ack-irreversible api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

## Stop And Ask First

Ask the user before live apply, before sending real conversion events, before activating or pausing serving, before changing budget or bids, before uploading audience data, and before any account-level change.

Do not use this skill for the broad OpenAI platform API, Ads Manager browser automation, or product-feed catalog upload over SFTP.
