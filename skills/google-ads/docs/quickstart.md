# Quickstart

Start with a small Google Ads read: checking accounts, presets, and campaign data before you touch spend.

Need more ideas? See [What you can do with Google Ads](use_cases.md). Need setup help? See [Connect your Google Ads account](onboarding.md).

A good first ask is:

> Show which Google Ads accounts I can access and confirm the customer IDs.

## What you will do first

1. Make sure the local tool can run.
2. Check the account or connection before asking for real work.
3. Run one small read and make sure the result matches the real service.
4. Ask for a reviewed plan before any change that could affect live data, spend, content, customers, or settings.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
google-ads-api-tool onboarding
```

```bash
google-ads-api-tool auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
google-ads-api-tool presets list
google-ads-api-tool presets show --preset optimization_pack_v1
google-ads-api-tool presets show --preset analysis_pack_v2
google-ads-api-tool presets show --preset analysis_pack_max_v1
google-ads-api-tool presets validate
```

```bash
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before budget, bid, campaign, audience, keyword, asset, upload, or account setting changes.

## What a useful first result includes

A good first result should make these things clear:

- what was checked
- whether the connection worked
- what came back from the service
- what the result means in plain English
- what is safe to inspect next
- where any saved file, export, plan, or receipt was written

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your Google Ads account](onboarding.md).
- For Google Ads workflow examples, read [Media buyer quickstart](media_buyer_quickstart.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
