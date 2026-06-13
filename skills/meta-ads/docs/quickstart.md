# Quickstart

Start with a small Meta Ads read: checking ad accounts, campaigns, creatives, and reporting data before you make media-buying decisions.

Need more ideas? See [What you can do with Meta Ads](use_cases.md). Need setup help? See [Connect your Meta Ads account](onboarding.md).

A good first ask is:

> Which ad accounts can this token read?

## What you will do first

1. Make sure the local tool can run.
2. Check the account, token, or public access the tool needs.
3. Run one small read and make sure the result matches the real service.
4. Review any local file path before saving exports or reports.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
cp .env.example .env
```

```bash
meta-ads-api-tool --output json --version
meta-ads-api-tool onboarding
meta-ads-api-tool --output json auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
meta-ads-api-tool --output json ad-accounts list --fields id,name
meta-ads-api-tool --output json --ad-account-id act_<id> campaigns list --fields id,name,status
meta-ads-api-tool --output json --ad-account-id act_<id> insights get --level campaign --fields campaign_id,impressions,clicks,spend --since 2026-01-01 --until 2026-01-31
meta-ads-api-tool --output json presets list
meta-ads-api-tool --output json snapshot export --ad-account-id act_<id> --preset ecom_core --since 2026-01-01 --until 2026-01-31 --out-dir ./exports --max-pages 2
meta-ads-api-tool --output json insights compare --ad-account-id act_<id> --level ad --fields ad_id,impressions,clicks,spend --since-a 2026-01-01 --until-a 2026-01-07 --since-b 2026-01-08 --until-b 2026-01-14
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Meta Ads is read-only here. Your first run should not change campaigns, budgets, ads, or audiences; only review any local export path before saving files.

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
- For setup details, read [Connect your Meta Ads account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
