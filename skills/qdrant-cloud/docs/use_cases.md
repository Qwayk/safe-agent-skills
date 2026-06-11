# Use cases

Use this page when you want ideas for real Qdrant Cloud jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run -> safe refusal for ordinary writes, or explicit provider backup/restore apply)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/provider receipts/logs) you can keep for proof and debugging

## Common use cases (examples)

- “Pull a report of the things that match these rules, and export it to a file.”
- “Find the right targets safely (avoid guessing), then propose changes for review.”
- “Prepare a large set of small metadata edits from a spreadsheet, then prove the tool requires explicit no-snapshot approval before a live write when no saved snapshot is available.”
- “Do a safe, repeatable transformation across many items, and prove it’s complete.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Apply only after explicit confirmation.
3) Refuse ordinary writes before Qdrant Cloud HTTP unless before-state or provider-backup capture exists.
4) For provider backup/restore, verify after apply and point to saved proof artifacts.
