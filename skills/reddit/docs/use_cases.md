# Use cases

Use this page when you want practical Reddit jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with Reddit work

Reddit work can affect public posts, communities, moderation, messages, and account state. The useful first step is usually to check what the API access can actually read and which official operations are available.

## Good jobs to give the agent

- “Check whether my Reddit OAuth setup is ready.”
- “List the official account or subreddit operations pinned in this tool.”
- “Read this subreddit or user endpoint and explain what came back.”
- “Check moderation, wiki, widget, message, or multi endpoints from the pinned docs set.”
- “Prepare a post, moderation, message, or account-state write plan and wait for my approval.”
- “Show the saved plan and run history for this request.”

## What the agent should show you

When you ask for a change, the agent should:

1. Show a dry-run plan first.
2. Name the account, subreddit, endpoint, and target record.
3. Confirm `--live` access before any real Reddit call.
4. Ask for stronger approval before risky or irreversible writes.
5. Say clearly when Reddit access, scopes, or User-Agent setup is missing.
