# Quickstart

This page helps you get one useful Meta Ads result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Meta Ads](use_cases.md). If setup is not done yet, read [Connect your Meta Ads account](onboarding.md).

A good first ask is:

> Which ad accounts can this token read?

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

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

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

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

## 4. Stop before changes

Meta Ads is read-only for normal use, so the first run should not change remote data. If a command writes local files, review the output path before running it.

## What good output looks like

A useful first result should tell you:

- what account, workspace, project, page, item, or public data was checked
- whether the tool connected successfully
- what the first read returned
- what the result means in normal language
- what is safe to do next
- where the plan, receipt, export, or saved file lives if the command created one

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your Meta Ads account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
