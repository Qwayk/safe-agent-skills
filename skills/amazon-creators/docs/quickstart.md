# Quickstart

This page helps you get one useful Amazon Creators result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Amazon Creators](use_cases.md). If setup is not done yet, read [Connect your account](onboarding.md).

A good first ask is:

> Gather every classification, variation summary, and parent ASIN for this set of ISBNs so I can compare paperback, hardcover, and Kindle formats.

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

## 1. Open the tool

If the skill is already installed in your agent host, start there. If you are working from source, follow the install notes in the repository before running commands.

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
amazon-creators-api-tool locales list
amazon-creators-api-tool items get --item-id B0EXAMPLE --resource-preset book-media
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

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
- For setup details, read [Connect your account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
