# Quickstart

This page helps you get one useful Unsplash result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Unsplash](use_cases.md). If setup is not done yet, read [Connect your Unsplash access key](onboarding.md).

A good first ask is:

> Can you find 20 photos for this topic and shortlist the best options?

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

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
unsplash-api-tool --output json onboarding
```

```bash
unsplash-api-tool --output json --version
unsplash-api-tool --output json auth check
unsplash-api-tool --output json photos search --query "minimal home office" --per-page 3
unsplash-api-tool --output json stats total
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
unsplash-api-tool --output json --yes export photos-list --out export.json --start-page 1 --max-pages 2 --per-page 10
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

A first change should stay as a preview or dry run until you approve it:

```bash
unsplash-api-tool --output json --plan-out plan.json photos download --id PHOTO_ID --dest downloads/photo.jpg
```

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
- For setup details, read [Connect your Unsplash access key](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
