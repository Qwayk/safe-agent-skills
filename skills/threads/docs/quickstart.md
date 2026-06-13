# Quickstart

Start with a small Threads read: checking profile and post data before you publish, reply, or moderate.

Need more ideas? See [What you can do with Threads](use_cases.md). Need setup help? See [Connect your Threads account](onboarding.md).

A good first ask is:

> Check my Threads profile and show recent owned posts.

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

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
threads-api-tool --output json --version
threads-api-tool --output json auth token status
threads-api-tool --output json auth check
threads-api-tool --output json profiles me
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
threads-api-tool search topic-tag --topic-tag <tag> [--fields <fields>] [--limit <n>] [--search-type <value>] [--search-mode <value>] [--media-type <value>]
threads-api-tool search recent-keywords
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before posts, replies, moderation, token changes, or anything that changes the live Threads account.

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
- For setup details, read [Connect your Threads account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
