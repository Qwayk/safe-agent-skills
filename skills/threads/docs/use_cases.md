# What you can do with Threads

Threads work usually starts with account identity and recent conversation context: profile, posts, replies, mentions, insights, and what the account is allowed to publish or moderate.

Ask the agent to confirm the account and read recent context before it prepares publishing, reply, repost, moderation, or delete work.

For setup, start with [Connect your Threads account](onboarding.md). For exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

- “Check my Threads profile and show recent owned posts.”
- “Look up a public Threads handle and list recent public posts.”
- “Show replies on this post and help me review the conversation.”
- “Pull media or user insights for this Threads account.”
- “Search a keyword or topic tag and show what Threads returns.”
- “Prepare a post or repost plan, but stop before any live write.”
- “Check location tagging or oEmbed data before we use it in a report.”

## What the agent should show you

When you ask for a change, the agent should:

1. Start with setup and auth checks when connection is unclear.
2. Read profile and post data before planning writes.
3. Show a dry-run plan for publishing, reposts, replies, moderation, or deletes.
4. Explain no-snapshot approval before token writes or Threads provider writes.
5. Point to plans and run summaries for follow-up review.
