# Use cases

Use this page when you want ideas for real Amazon Creators jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with Amazon catalog research

Amazon Creators work often means comparing books, formats, browse nodes, and locale-specific catalog data before a decision is made:

- Bulk research on books, catalogs, and browse nodes without clicking around Amazon’s UI.
- Preview-first workflows where the agent shows you a dry-run plan, then only calls Amazon after you confirm.
- Deterministic behavior: the agent refuses when the request would be unclear instead of guessing.
- Audit artifacts (plans, receipts, run logs) that you can share as proof or debugging signals.

## Common outcomes you can ask the agent for

- “Gather every classification, variation summary, and parent ASIN for this set of ISBNs so I can compare paperback, hardcover, and Kindle formats.”
- “Document the browse-node hierarchy for a niche category so we know the canonical navigation path before we redesign the catalog copy.”
- “Confirm the locale mapping before we place an order so the marketplace header matches the region we care about.”
- “Collect simplified technical info for multiple formats and send me both the plan (dry-run) and the receipt once the live data arrives.”

## What you’ll see from the agent (trust + safety)

When you ask for a catalog request, the agent should:

1) Show a dry-run plan that lists the locale, marketplace resources, and parameters before any live traffic.
2) Pause for your confirmation so no direct call to Amazon happens until you explicitly approve.
3) After the confirmation, return a simplified data view, a request summary, and a receipt (plus optional files if requested) so you can audit what was fetched.
4) Keep tokens, secrets, and raw headers out of the logs; you can share the plan/receipt safely.
