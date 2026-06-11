# Use cases

Use this page when you want ideas for real Threads jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## What this tool is for

- Inspect account identity and profile metadata for an authenticated Threads user.
- Read posts, media, and publishing limit data before deciding what to publish.
- Plan reply actions (`replies`, `conversation`, `pending_replies`) and mentions handling.
- Get posts/media insight snapshots and location/search/oEmbed lookups.

## What the agent should do first

1) `onboarding`
2) `auth check`
3) Read-only profile and posts checks
4) Dry-run plan for any write action
5) If apply is requested, collect the safety refusal and confirm no write happened

## Safety expectation from the agent

- Show dry-run first for write requests.
- Explain that current apply attempts require explicit no-snapshot approval before provider writes or successful receipts.
- Use plans, refusal output, and saved run summaries for follow-up review.
