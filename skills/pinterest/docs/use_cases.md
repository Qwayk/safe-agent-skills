# Use cases

Use this page when you want ideas for real Pinterest jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

No‑code tools can do simple scheduled exports. This tool is built for:

- Deep inventory snapshots (boards, sections, pins) with stable JSON exports
- Repeatable audits you can re-run and compare over time
- Safety-gated write planning (link hygiene and other write families require explicit no-snapshot approval before live changes for now)

## Common use cases (examples)

### Inventory and audits (read-only to Pinterest)

- “Export a full snapshot of my account (boards, sections, pins) into a folder.”
- “Generate a ‘boards summary’ report (board privacy, section counts, pin counts).”
- “Create a periodic audit snapshot so I can track changes over time.”

### Ads performance snapshots (read-only)

- “Export my ad account structure (campaigns, ad groups, ads) to a folder so I can review it with my team.”
- “Take a weekly ‘ads inventory snapshot’ so I can detect unexpected changes in campaigns or ad group settings.”
- “Export aggregated ads analytics (no user-level/event-level data) for a date range so I can spot performance changes.”

Note: Ads endpoints require access to a Pinterest ad account and may require additional scopes/tiers.

### Catalog health and feeds (read-only)

- “List my product catalogs and feeds, and export their processing results so I can spot feed issues.”
- “Create a recurring ‘catalogs snapshot’ so I can track feed changes and product group configuration over time.”
- “Export product group products + item issues so I can identify catalog ingestion problems.”
- “List catalog reports / stats (if enabled for my account/scopes).”

### Analytics (read-only)

- “Show me my top pins and account analytics for the last 90 days (if enabled for my account/scopes).”

### Pin link hygiene planning

- “Plan link canonicalization for these pins and show me exactly what would change.”
- “Show the missing-approval refusal for a confirmed apply attempt so I can see that no Pinterest write happened without approval.”

## What you’ll see from the agent (trust + safety)

For write operations, the agent should:

1) Produce a plan (dry-run).
2) Explain the no-snapshot limit when no saved snapshot is available.
3) Apply only after explicit no-snapshot approval, or confirm that a missing-approval refusal sent no Pinterest write.
