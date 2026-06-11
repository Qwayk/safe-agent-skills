# Use cases

Use this page when you want ideas for real Shopify Admin jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with store operations

Shopify work usually means reviewing a live catalog, planning many changes together, and keeping proof of what was proposed before anything touches the store:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run plans; live apply requires explicit no-snapshot approval when no saved snapshot is available)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans, refusals, and logs) you can keep for proof and debugging

## Common use cases (examples)

- “Pull a report of the things that match these rules, and export it to a file.”
- “Find the right targets safely (avoid guessing), then propose changes for review.”
- “Create dry-run plans for a large set of small metadata edits from a spreadsheet.”
- “Do a safe, repeatable transformation across many items, and prove it’s complete.”

## Shopify Admin-specific examples (still plain English)

These examples are intentionally specific so you can understand what the tool is capable of without learning the Shopify Admin API.

- Products: “Create a dry-run plan for a product with variants and prices.”
- Products: “Draft a plan to update product titles, descriptions, tags, and media for these product IDs.”
- Inventory: “Set on-hand inventory levels for these SKUs at this location.”
- Orders: “Export orders from the last 30 days with line items and totals, then save to a file.”
- Refunds: “Draft a refund mutation plan, review the recovery limit, then approve the exact live apply only if it still looks right.”
- Discounts: “Create a dry-run plan for a discount code with these rules and an end date.”
- Collections: “Plan adding these products to this collection and removing others.”
- Customers: “Find customers who match this segment and export their IDs.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Explain any extra mutation gates, including `--ack-no-snapshot` when no saved snapshot exists.
3) Apply only after explicit approval, then report the receipt or any provider error clearly.
4) Point to the saved plan and run artifacts.
