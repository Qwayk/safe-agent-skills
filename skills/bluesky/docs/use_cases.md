# What you can do with Bluesky

Use this page when you want ideas for real Bluesky jobs to hand to your agent.
If you need setup first, start with [Connect your Bluesky account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill is best when you want a careful agent path into documented Bluesky API work instead of guessing from scattered docs.

## Common jobs this skill is good at

- Check a profile, DID, repo, or basic account state.
- Review recent posts, lists, follows, or feed-related data.
- Inspect the operation inventory before choosing a Bluesky endpoint.
- Preview a post, record, or account write before any live apply.
- Review moderation, chat, or admin surfaces when your account already has that access.
- Capture raw subscription frames when you need stream-style inspection.

## Real example asks

- "Check this Bluesky profile and show me the recent post surface safely."
- "List the documented operations for the area I need before we choose one."
- "Preview the exact write plan for creating or updating a record, but do not apply it yet."
- "Show me the safest live read for this endpoint before we do anything riskier."

## Why this is useful

- The tool keeps reads and writes explicit instead of hiding them behind vague prompts.
- You can inspect the operation inventory before the agent touches a live endpoint.
- Write work leaves behind plans, refusals, receipts, and run history for review.

## What a careful run should look like

- Start with auth and one small live read.
- Review the exact endpoint and payload before any write apply.
- Use live apply only after the plan looks right.
- Treat missing before-state and irreversible actions as slower approval points, not as normal clicks.
