---
name: openai-ads
description: Use when the user asks an agent to check, report on, prepare, or carefully change ChatGPT Ads / OpenAI Ads campaigns, ad groups, ads, insights, targeting, product-feed setup, custom audiences, files, conversions, pixels, image tags, or server-side conversion events.
---

# OpenAI Ads

Use this skill for ChatGPT Ads / OpenAI Ads account work.

A user may ask for things like campaign stats, ads that are not running, a new paused campaign, audience review, tracking checks, product-feed guidance, or a server-side conversion event plan.

Start by reading. Good first actions are:

```bash
openai-ads-safe-agent-cli --output json api list
openai-ads-safe-agent-cli onboarding
openai-ads-safe-agent-cli auth check
openai-ads-safe-agent-cli api campaigns list-campaigns --query limit=10
openai-ads-safe-agent-cli measurement events-list
```

If the user asks for a live change, show the planned change first. Do not continue until the user approves it.

Plan example:

```bash
openai-ads-safe-agent-cli --plan-out plan.json api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

Apply only after the user reviews the saved plan:

```bash
openai-ads-safe-agent-cli --apply --yes --plan-in plan.json --ack-no-snapshot --ack-irreversible api campaigns create-campaign --body-json '{"name":"West Coast test","status":"paused"}'
```

Ask before creating, updating, pausing, activating, archiving, uploading, changing budgets or bids, changing targeting, changing audiences, changing account settings, or sending real conversion events.

Do not print API keys, conversion API keys, private Pixel IDs, audience rows, customer IDs, raw emails, external IDs, or tracking URLs with private parameters.

Do not use this skill for normal OpenAI Platform API work, Ads Manager browser automation, or product-feed catalog upload over SFTP.
