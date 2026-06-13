# Quickstart

Start with a small Instantly read: checking campaigns, leads, sending health, and weak spots before you change outreach.

Need more ideas? See [What you can do with Instantly](use_cases.md). Need setup help? See [Connect your Instantly account](onboarding.md).

A good first ask is:

> Which active campaigns look weak or risky this week?

## What you will do first

1. Make sure the local tool can run.
2. Check the account or connection before asking for real work.
3. Run one small read and make sure the result matches the real service.
4. Ask for a reviewed plan before any change that could affect live data, spend, content, customers, or settings.

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
instantly-api-tool onboarding
```

```bash
instantly-api-tool --output json auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
instantly-api-tool --output json whoami
instantly-api-tool --output json campaigns list --limit 10
```

```bash
instantly-api-tool --output json analytics campaigns --start-date 2026-06-01 --end-date 2026-06-07
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before campaign, lead, sending, duplicate, bulk, or message changes.

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
- For setup details, read [Connect your Instantly account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
