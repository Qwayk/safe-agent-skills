# Use cases

Use this page when you want ideas for real Google Search Console jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run → explicit apply → verification)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/receipts/logs) you can keep for proof and debugging

## Common use cases (examples)

- “List all verified sites in my Search Console account and tell me which ones look relevant.”
- “Run Search Analytics queries for a site and export the results (queries, pages, countries, devices).”
- “Inspect a URL (index status) and summarize what Google thinks about it.”
- “Submit one or more sitemap URLs, but show me a dry-run plan first and only apply after approval.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Apply only after explicit confirmation.
3) Verify after apply (read-back or idempotence).
4) Provide a short receipt and point to any saved proof artifacts.
