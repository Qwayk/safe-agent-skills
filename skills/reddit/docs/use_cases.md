# What you can do with Reddit

Reddit work can affect public posts, communities, moderation, messages, and account state. Start by checking what the API access can read and which official operations are available before asking for any write plan.

For setup, start with [Connect your account](onboarding.md). For exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

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
