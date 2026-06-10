# Use cases

Use this page when you want ideas for real Microsoft Ads jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). A safe agent CLI is built for:

- Bulk work on existing libraries (hundreds/thousands of records)
- Preview-first changes (dry-run -> explicit approval when needed -> receipt or honest blocker)
- Deterministic behavior (refuses when unsure instead of guessing)
- Audit artifacts (plans/refusals/logs) you can keep for proof and debugging

## Common use cases (examples)

- “Pull a report of performance metrics for my account and export it to a file.”
- “Find the right targets safely (avoid guessing), then propose changes for review.”
- “Prepare a large set of small metadata edits from a spreadsheet, then show the plan and approval needed before any write runs.”
- “Do a safe, repeatable transformation across many items, and prove it’s complete.”

## Microsoft Ads-specific examples (still plain English)

These examples are intentionally specific so you can understand what the tool is capable of without learning the API.

- Keyword research: “Estimate keyword search volume and traffic estimates for these keywords, then export a table.”
- Audience and targeting: “Get audience estimation and breakdown for this audience definition, then summarize the results.”
- Opportunities and recommendations: “List recommendations for my account, show me which ones are safe, then generate a plan.”
- Reporting: “Generate a performance report for the last 30 days and save it to a file for analysis.”
- Bulk workflows: “Download my campaigns, edit names and budgets in a spreadsheet, then generate a plan and confirm no write is sent yet.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Show whether before-state was saved, a provider backup exists, or no useful before-copy can be saved.
3) Ask for explicit no-snapshot approval when needed, then proceed with approved supported writes or refuse for a real blocker.
4) Point to the saved plan, receipt or refusal, run summary, and audit log.
