# Quickstart

This technical command path helps you get one useful Hacker News result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Hacker News](use_cases.md). If setup is not done yet, read [Use Hacker News with no account](onboarding.md).

A good first ask is:

> Show me the current top stories, fetch the first five items, and tell me the main topics people are discussing.

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

Hacker News does not need a private account for the first public read. Still run the local check so you know the command works.

```bash
hacker-news-api-tool --output json --version
hacker-news-api-tool --output json onboarding
hacker-news-api-tool --output json auth check
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
hacker-news-api-tool --output json stories top
hacker-news-api-tool --output json items get --id 8863
hacker-news-api-tool --output json users get --id pg
hacker-news-api-tool --output json updates get
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

Hacker News is read-only for normal use, so the first run should not change remote data. If a command writes local files, review the output path before running it.

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
- For setup details, read [Use Hacker News with no account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
