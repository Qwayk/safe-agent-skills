# Quickstart

Start with a small Skimlinks read: checking merchants, reports, links, and product data before you build affiliate content.

Need more ideas? See [What you can do with Skimlinks](use_cases.md). Need setup help? See [Connect your Skimlinks account](onboarding.md).

A good first ask is:

> Which merchants are active for this country or vertical?

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
cp .env.example .env
```

```bash
skimlinks-safe-cli onboarding
```

```bash
skimlinks-safe-cli --output json --version
skimlinks-safe-cli onboarding
skimlinks-safe-cli auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
skimlinks-safe-cli merchant merchants list --search laptop --country US --limit 10
```

```bash
skimlinks-safe-cli reporting link-report query --start-date 2026-01-01 --end-date 2026-01-31 --dim merchant_id --met clicks
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Skimlinks is mostly read or read-like here. Review generated wrapper links, report exports, product-key results, and any local file path before using them publicly.

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
- For setup details, read [Connect your Skimlinks account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
