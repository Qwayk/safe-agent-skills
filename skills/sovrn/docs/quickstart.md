# Quickstart

Start with a small Sovrn read: checking Commerce and Advertising data before you build publisher reports or links.

Need more ideas? See [What you can do with Sovrn](use_cases.md). Need setup help? See [Connect your Sovrn account](onboarding.md).

A good first ask is:

> Check whether the Sovrn credentials are ready, then show which Commerce and Advertising areas can be used.

## What you will do first

1. Make sure the local tool can run.
2. Check the account, token, or public access the tool needs.
3. Run one small read and make sure the result matches the real service.
4. Review any local file path before saving exports or reports.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
sovrn-safe-cli onboarding
```

```bash
sovrn-safe-cli --output json --version
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
sovrn-safe-cli commerce campaigns get --search PRIMARY
```

```bash
sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Sovrn is read-only here even when some provider endpoints use POST for reports. Your first run should not change remote data; only review local export paths.

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
- For setup details, read [Connect your Sovrn account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
