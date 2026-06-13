# Quickstart

Start with a small Amazon Product Advertising API read: checking real Amazon product matches before you build a gift guide, comparison, or affiliate page.

Need more ideas? See [What you can do with Amazon Product Advertising API](use_cases.md). Need setup help? See [Connect your Amazon Associates credentials](onboarding.md).

A good first ask is:

> Which products are worth considering for this gift guide?

## What you will do first

1. Make sure the local tool can run.
2. Check the account, token, or public access the tool needs.
3. Run one small read and make sure the result matches the real service.
4. Review any local file path before saving exports or reports.

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

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
amazon-pa-api-tool --output json product get --asin B000000000
```

```bash
amazon-pa-api-tool --output json product resolve --url "https://www.amazon.com/dp/B000000000/"
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

This tool is read-only for Amazon product data. Your first run should not change Amazon or Associates data; only review local export paths before saving files.

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
- For setup details, read [Connect your Amazon Associates credentials](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
