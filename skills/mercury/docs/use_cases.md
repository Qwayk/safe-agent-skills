# Use cases

Use this page when you want ideas for real Mercury jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## What this tool does (plain English)

- It **reads** data from the Mercury API (accounts, transactions, statements, invoices, and more).
- It **never changes anything inside Mercury** (GET-only by design).
- If you approve it, it can **save exports/downloads to your computer** (local file writes only).

## Common Mercury use cases (examples)

These are plain-English requests you can give your agent:

- “Export all transactions from January 1 to December 31 to a CSV for my accountant (dry-run plan first).”
- “List all my Mercury accounts and show the account IDs.”
- “Download statement PDFs for a specific account so I can reconcile monthly.”
- “List invoices and download the PDF for invoice X.”
- “Download an invoice attachment to my computer (dry-run first, then apply).”
- “Pull the last N events so I can audit activity.”

## What you’ll see from the agent (trust + safety)

When you ask for an export or download, the agent should:

1) Show a dry-run preview of what would happen.
2) Apply only after explicit confirmation.
3) Verify the local file(s) were written successfully.
4) Provide a short receipt and point to the saved proof artifacts.
