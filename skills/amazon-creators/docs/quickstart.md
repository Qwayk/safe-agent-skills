# Quickstart

Start with a small Amazon Creators read: checking catalog details, ASIN variations, and creator research before you save or upload anything.

Need more ideas? See [What you can do with Amazon Creators](use_cases.md). Need setup help? See [Connect your Amazon Creators account](onboarding.md).

A good first ask is:

> Gather every classification, variation summary, and parent ASIN for this set of ISBNs so I can compare paperback, hardcover, and Kindle formats.

## What you will do first

1. Make sure the local tool can run.
2. Check the account or connection before asking for real work.
3. Run one small read and make sure the result matches the real service.
4. Ask for a reviewed plan before any change that could affect live data, spend, content, customers, or settings.

## 1. Open the tool

If the skill is already installed in your agent host, start there. If you are working from source, follow the install notes in the repository before running commands.

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
amazon-creators-api-tool locales list
amazon-creators-api-tool items get --item-id B0EXAMPLE --resource-preset book-media
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before token changes, uploads, generated catalog files, or any action that changes local account setup.

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
- For setup details, read [Connect your Amazon Creators account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
