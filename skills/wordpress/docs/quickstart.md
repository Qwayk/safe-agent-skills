# Quickstart

Start with a small WordPress read: checking posts, pages, media, users, and site content before you edit or publish.

Need more ideas? See [What you can do with WordPress](use_cases.md). Need setup help? See [Connect your WordPress site](onboarding.md).

A good first ask is:

> Find all posts/pages mentioning a keyword and give me a report with links, status, and last modified date.

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
wordpress-api-tool --version
wordpress-api-tool auth check
wordpress-api-tool discover post-types
wordpress-api-tool discover statuses
wordpress-api-tool discover taxonomies
wordpress-api-tool comments list --limit 3
wordpress-api-tool search query --query "hello" --limit 3
wordpress-api-tool terms list --taxonomy categories --query "news" --limit 5
wordpress-api-tool media find --query "banner" --limit 5
wordpress-api-tool post find --query "test" --limit 5
wordpress-api-tool post get --slug hello-world
wordpress-api-tool post truth --slug hello-world --resolve-urls
wordpress-api-tool post images --slug hello-world --include-featured
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
wordpress-api-tool search query --query "hello" --limit 3
wordpress-api-tool post find --query "test" --limit 5
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before post, page, media, user, taxonomy, plugin, or site setting changes.

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
- For setup details, read [Connect your WordPress site](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
