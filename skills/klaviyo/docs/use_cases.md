# Use cases

Use this page when you want ideas for real Klaviyo jobs to hand to your agent.
If you need setup first, start with [Connect your Klaviyo account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is useful for Klaviyo work

Most no-code tools are fine for one small trigger. This skill is built for bigger Klaviyo jobs like:

- One explicit command surface across the stable Klaviyo API
- Bulk work across profiles, lists, segments, catalogs, coupons, templates, and campaigns
- Preview-first changes with a dry-run plan before live apply
- Clear safety stops when a change is risky or recovery is limited
- Saved plans, receipts, refusals, and logs you can keep as proof

## Common Klaviyo jobs

- "Show me which lists, segments, forms, or campaigns match these filters."
- "Check one profile, event stream, or metric before I change anything."
- "Prepare a safe bulk import, subscribe, suppress, or unsubscribe change, then show the plan for review."
- "Plan catalog, coupon, template, webhook, or form changes from reviewed JSON."
- "Plan a send cancellation or delete action and show me the recovery limit before apply."
- "Use the client endpoints for signup, reviews, push tokens, or event capture when I only have the company id."

## What you should expect from the agent

When you ask for a change, the agent should:

1. Show a dry-run preview of what would change.
2. Explain the recovery limit before any live write runs.
3. Require explicit no-snapshot approval when no saved snapshot is available.
4. Refuse apply safely if someone skips the required approval gates.
5. Point to the saved plan, receipt or refusal summary, and proof files.
