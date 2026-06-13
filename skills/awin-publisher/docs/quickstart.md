# Quickstart

Start with a small Awin Publisher read: checking publisher accounts, merchants, reports, links, and feed data before you create or upload anything.

Need more ideas? See [What you can do with Awin Publisher](use_cases.md). Need setup help? See [Connect your Awin publisher account](onboarding.md).

A good first ask is:

> Which publisher accounts can this token see?

## What you will do first

1. Make sure the local tool can run.
2. Check the account or connection before asking for real work.
3. Run one small read and make sure the result matches the real service.
4. Ask for a reviewed plan before any change that could affect live data, spend, content, customers, or settings.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
cp .env.example .env
awin-publisher-safe-cli onboarding
awin-publisher-safe-cli --output json auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
awin-publisher-safe-cli --output json accounts list
awin-publisher-safe-cli --output json programs list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json offers list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json transactions list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-02T00:00:00Z --timezone UTC
awin-publisher-safe-cli --output json reports advertiser --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before uploads, proof-of-purchase work, report exports, or anything that changes publisher-side data.

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
- For setup details, read [Connect your Awin publisher account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
