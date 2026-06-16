# What you can do with Bluesky

Bluesky work can touch public posts, follows, lists, records, chat, and moderation. The safest first move is to inspect the account and endpoint before planning any write.

These are good starting points when you want an agent to review a Bluesky account, explain what it can safely read, or prepare a change without applying it too early.

For setup, start with [Connect your Bluesky account](onboarding.md). For exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

- "Check this Bluesky profile and show me the recent post surface safely."
- "List the documented operations for the area I need before we choose one."
- "Preview the exact write plan for creating or updating a record, but do not apply it yet."
- "Show me the safest live read for this endpoint before we do anything riskier."
- "Review lists, follows, feeds, or chat surfaces available to this account."
- "Capture raw subscription frames if I need stream-style inspection."

## What the agent should show you

When you ask for a change, the agent should:

1. Start with auth and one small live read.
2. Name the endpoint, payload, account, and target record.
3. Show the dry-run plan before any write apply.
4. Ask for stronger approval for risky, irreversible, or no-snapshot writes.
5. Point to the plan, receipt, refusal, or run history after the request.
