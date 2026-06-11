# Use cases

Use this page when you want ideas for real Threads jobs to hand to your agent.
If you need setup first, start with [Connect your Threads account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## What this tool is for

- Inspect account identity and profile metadata for an authenticated Threads user.
- Read posts, media, and publishing limit data before deciding what to publish.
- Plan reply actions (`replies`, `conversation`, `pending_replies`) and mentions handling.
- Get posts/media insight snapshots and location/search/oEmbed lookups.

## Common use cases

- “Check my Threads profile and show recent owned posts.”
- “Look up a public Threads handle and list recent public posts.”
- “Show replies on this post and help me review the conversation.”
- “Pull media or user insights for this Threads account.”
- “Search a keyword or topic tag and show what Threads returns.”
- “Prepare a post or repost plan, but stop before any live write.”

## What the agent should do first

1) `onboarding`
2) `auth check`
3) Read-only profile and posts checks
4) Dry-run plan for any write action
5) If apply is requested, explain the extra no-snapshot approval before anything writes

## Safety expectation from the agent

- Show dry-run first for write requests.
- Explain that token writes and Threads provider writes need explicit no-snapshot approval when no saved snapshot exists.
- Use plans and saved run summaries for follow-up review.
