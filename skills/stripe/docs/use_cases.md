# Use cases

Use this page when you want ideas for real Stripe jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with Stripe work

Stripe work usually means checking live billing data carefully, sorting through lots of records, and slowing down before anything touches money or customer billing. This tool is built for:

- Bulk work on existing records like customers, subscriptions, invoices, products, and payouts
- Preview-first changes where the agent shows the plan before any live Stripe write
- Deterministic behavior that refuses when unsure instead of guessing
- Proof artifacts like plans, refusals, and receipts that you can keep for review and debugging

## Common use cases (examples)

- “Show me recent customers, subscriptions, invoices, and failed payments, then export the results to a file.”
- “Find the Stripe records that match these rules and prepare the safe next step for review.”
- “Create dry-run plans for metadata or catalog updates across many items from a spreadsheet.”
- “Review payouts, refunds, disputes, or transfers and tell me what needs attention before we do anything live.”

## Stripe-specific examples (still plain English)

- Customers: “List recent customers with email, creation date, and account status.”
- Subscriptions: “Show subscriptions that are trialing, past due, or canceled in the last 30 days.”
- Invoices: “Export open and uncollectible invoices so I can review follow-up work.”
- Products and prices: “Draft a metadata update plan for these product or price IDs and stop before any writes.”
- Refunds: “Prepare a refund plan for this payment and explain every approval gate before live apply.”
- Payouts and transfers: “Review recent payouts and transfers and flag anything unusual.”
- Connect: “Check this connected account safely and show me what data is available before we plan any changes.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Explain any extra approval gates, especially for money-moving or irreversible work.
3) Ask for explicit no-snapshot approval when Stripe work has no saved snapshot or provider backup.
4) Point to the saved plan, receipt, or run artifacts.
