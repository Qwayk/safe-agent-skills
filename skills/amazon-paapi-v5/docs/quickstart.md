# Quickstart

This page helps you get one useful Amazon Product Advertising API result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Amazon Product Advertising API](use_cases.md). If setup is not done yet, read [Connect your Amazon Associates credentials](onboarding.md).

A good first ask is:

> Which products are worth considering for this gift guide?

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
amazon-pa-api-tool --output json --version
amazon-pa-api-tool --output json auth check
amazon-pa-api-tool --output json product search --query "cast iron skillet" --limit 3
```

```bash
PYTHONPATH=src python3 -m amazon_pa_api_tool --output json auth check
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
amazon-pa-api-tool --output json product get --asin B000000000
```

```bash
amazon-pa-api-tool --output json product resolve --url "https://www.amazon.com/dp/B000000000/"
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

A first change should stay as a preview or dry run until you approve it:

```bash
amazon-pa-api-tool --output json jobs run --file jobs.csv
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
- For setup details, read [Connect your Amazon Associates credentials](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
