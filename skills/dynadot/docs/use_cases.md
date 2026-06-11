# Use cases

Use this page when you want ideas for real Dynadot jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run -> explicit apply attempt -> explicit no-snapshot approval today)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/logs) you can keep for proof and debugging

## Common use cases (examples)

- “Pull a report of the things that match these rules, and export it to a file.”
- “Plan a push of hundreds of domains to another Dynadot account, then show why apply requires explicit no-snapshot approval when no saved snapshot is available.”
- “Find the right targets safely (avoid guessing), then propose changes for review.”
- “Plan a large set of metadata edits from a spreadsheet, then confirm the tool requires explicit no-snapshot approval before writing.”
- “Do a safe, repeatable transformation across many items, and prove it’s complete.”

More Dynadot-specific examples:
- “Show me all my domains, and flag anything expiring soon.”
- “For these domains, show current name servers and DNS, then propose what to change.”
- “Turn WHOIS privacy on/off for this list of domains (preview first; apply requires explicit no-snapshot approval).”
- “Monitor marketplace listings / auctions and export a daily report.”
- “Generate transfer auth codes (treat them as sensitive) and save them to a private file.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Try apply only after explicit confirmation.
3) Confirm the explicit no-snapshot approval and that nothing changed.
4) Point to any saved proof artifacts.
