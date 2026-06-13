# Quickstart

Start with a small Hacker News read: checking live story lists, comments, users, and updates without scraping the website.

Need more ideas? See [What you can do with Hacker News](use_cases.md). Need setup help? See [Use Hacker News with no account](onboarding.md).

A good first ask is:

> Show me the current top stories, fetch the first five items, and tell me the main topics people are discussing.

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

Hacker News does not need a private account for the first public read. Still run the local check so you know the command works.

```bash
hacker-news-api-tool --output json --version
hacker-news-api-tool --output json onboarding
hacker-news-api-tool --output json auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
hacker-news-api-tool --output json stories top
hacker-news-api-tool --output json items get --id 8863
hacker-news-api-tool --output json users get --id pg
hacker-news-api-tool --output json updates get
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Hacker News is read-only here and needs no account. The first run should not change anything; just fetch real items before summarizing trends.

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
- For setup details, read [Use Hacker News with no account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
