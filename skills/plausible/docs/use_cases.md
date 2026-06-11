# Use cases

Use this page when you want ideas for real Plausible jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no-code automation)

No-code tools can pull a single metric on a schedule. This tool is built for:

- Deep analytics queries (custom metrics/dimensions, funnels, comparisons)
- Repeatable reporting (weekly/monthly snapshots)
- Careful writes (site changes start as plans; event sends need explicit approval because they cannot be undone automatically)
- Receipts you can keep for auditing what was run

## Common use cases (examples)

### Reporting (read-only)

- “Generate a weekly report: top pages, sources/referrers, devices, and goal conversions.”
- “Create a ‘membership funnel’ report for the last 30 days and compare to the previous period.”
- “Run this Stats query JSON, validate it first, and export results to a file.”

### Analytics QA

- “Verify tracking is working by checking recent traffic on a specific page path.”
- “Find top entry and exit pages for the last 14 days.”

### Events (writes analytics; only with explicit approval)

- “Plan a test event to validate my conversion pipeline, but don’t send it until I approve.”
- “Send the test event with verification, and show me a receipt of what was written.”

## What you’ll see from the agent (trust + safety)

When you ask for anything that writes analytics data, the agent should:

1) Show a dry-run plan.
2) Apply only after explicit confirmation.
3) Ask for extra acknowledgement when the action has no automatic restore point.
4) Verify best-effort (when supported) and provide a receipt.
