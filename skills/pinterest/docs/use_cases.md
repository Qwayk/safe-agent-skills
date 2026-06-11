# What you can do with Pinterest

Use this page when you want ideas for real Pinterest work to hand to your agent.
If you need setup first, start with [Connect your Pinterest account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## A good first ask

"Check the Pinterest skill is configured, export a snapshot of my boards and pins, and tell me if anything looks unusual before we plan changes."

## Common Pinterest jobs

### Inventory and audits

- "Export a full snapshot of my boards, sections, and pins into a folder."
- "Generate a boards summary so I can review board privacy, section counts, and pin counts."
- "Create a repeatable audit snapshot so I can compare account structure over time."

### Analytics and performance review

- "Show me my top pins and account analytics for the last 90 days if my account supports it."
- "Export my ads account structure so I can review campaigns, ad groups, and ads with my team."
- "Pull aggregated ads analytics for this date range so I can spot performance changes."

### Catalog and feed diagnostics

- "List my catalogs and feeds, then show the latest processing results."
- "Export product group products and item issues so I can diagnose catalog problems."
- "Show me catalog reports or stats for this ad account."

### Careful change planning

- "Plan a pin-link cleanup for these pins and show me exactly what would change."
- "Preview the write steps for a board, pin, ad, or feed change before anything goes live."
- "Show the missing-approval refusal first so I can confirm nothing writes without approval."

## Why this skill is useful

- It gives you stable inventory snapshots instead of one-off screenshots or manual exports.
- It helps your agent inspect Pinterest account structure before it suggests changes.
- It keeps risky write work in plan-first mode when there is no saved before-state yet.

## What you should expect from the agent

For normal reads and snapshots, the agent should fetch the data and summarize what matters.

For write-capable operations, the agent should:

1. produce a dry-run plan first
2. explain the no-snapshot limit clearly
3. wait for explicit approval before any live Pinterest write
4. show refusal output when a missing approval stopped the write before Pinterest HTTP
