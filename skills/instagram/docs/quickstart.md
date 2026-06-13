# Quickstart

Start with a small Instagram read: checking professional account access, media, comments, and insights before you post or moderate anything.

Need more ideas? See [What you can do with Instagram](use_cases.md). Need setup help? See [Connect your Instagram access](onboarding.md).

A good first ask is:

> Show which Instagram professional account this token reaches and list my latest media.

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
instagram-api-tool onboarding
```

```bash
instagram-api-tool auth check
instagram-api-tool users me --fields user_id,username,account_type
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see that the connection works and that the agent is looking at the right account, page, item, or public record.

```bash
instagram-api-tool media list --ig-user-id 17841400000000000 --fields id,caption,media_type,permalink --limit 10
```

```bash
instagram-api-tool comments list --media-id 17900000000000000 --fields id,text,username,timestamp
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before anything risky

Ask for a reviewed plan before media publishing, comment actions, message actions, token changes, or moderation work.

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
- For setup details, read [Connect your Instagram access](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).
