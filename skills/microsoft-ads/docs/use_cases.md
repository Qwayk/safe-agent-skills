# Use cases

Use this page when you want ideas for real Microsoft Ads jobs to hand to your agent.
If you need setup first, start with [Connect your Microsoft Ads account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Common use cases

- "Check my Microsoft Ads setup and confirm which live reads are safe to run first."
- "Pull a performance report for the last 30 days and save it for review."
- "Review campaigns, budgets, bids, or recommendations before we change anything."
- "Estimate keyword traffic or audience size before we build a plan."
- "Prepare a bulk or service-operation change from a request file and show me the plan first."
- "Show me the approval path for a higher-risk budget or delete-like action before anything goes live."

## Why this skill is more useful than raw docs

This skill gives your agent a safer path through real Microsoft Ads API work.

- It can keep every real network call behind `--live`.
- It can show a dry-run plan before service-operation or batch changes.
- It can help with account review, reporting, and bulk workflows without turning you into a SOAP expert first.
- It can leave plans, refusals, receipts, run history, docs, and tests in one place so you can inspect what happened.
- It can require explicit no-snapshot approval when there is no useful saved before-state for the write.

## What this skill intentionally does not promise

- It does not promise a built-in undo path for every Microsoft Ads write.
- It does not guess the right account IDs, request JSON, or target when the input is unclear.
- It does not promise that Microsoft bulk or reporting jobs finish instantly.
