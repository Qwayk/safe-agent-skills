# Use cases

Use this page when you want ideas for real YouTube jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing channels and libraries (hundreds/thousands of items)
- Preview-first changes (plan/dry-run -> explicit approval when needed -> receipt or honest blocker)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/logs) you can keep for proof and debugging

## Common YouTube use cases (examples)

- Reporting and inventory
  - “List the latest uploads on this channel, including titles and publish dates, then export a CSV.”
  - “Find videos with a specific keyword in the title/description and summarize what needs updating.”
- Video publishing and metadata updates
  - “Plan a private video upload with a draft title/description, then show me the approval needed before any upload happens.”
  - “Preview title/description/tag updates from a spreadsheet, then confirm whether before-state, no-snapshot approval, or a true blocker applies.”
- Playlists and organization
  - “Plan a new playlist and video order, then wait for my approval before anything changes.”
  - “Audit playlists: find duplicates, missing videos, or incorrect ordering and propose fixes.”
- Comments and moderation
  - “Pull recent comment threads for these videos and flag anything that violates the policy.”
  - “Plan templated replies to comments, then confirm the write attempt requires explicit no-snapshot approval before posting.”
- Captions and localization
  - “Download captions for these videos for a localization workflow.”
  - “Plan updated caption track uploads, then confirm no upload endpoint is called.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Attempt only after explicit confirmation.
3) Require explicit no-snapshot approval before provider writes/uploads when no saved snapshot is available.
4) Provide a receipt or short refusal summary and point to saved proof.
