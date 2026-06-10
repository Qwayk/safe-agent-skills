# Use cases

Use this page when you want ideas for real Google Analytics jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first write-like requests with apply refusal before GA4 HTTP
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/logs) you can keep for proof and debugging

## Common use cases (examples)

- “Pull a report of the things that match these rules, and export it to a file.”
- “Find the right targets safely (avoid guessing), then propose changes for review.”
- “Plan a large set of small metadata edits from a spreadsheet, then confirm apply requires explicit no-snapshot approval before GA4 writes.”
- “Do a safe, repeatable transformation across many items, and prove it’s complete.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Apply only after explicit confirmation.
3) Confirm apply refusal before GA4 HTTP.
4) Point to the saved plan, audit log, and run summary.
