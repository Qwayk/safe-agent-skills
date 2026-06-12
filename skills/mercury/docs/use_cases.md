# What you can do with Mercury

Mercury work usually starts with finance review questions: what accounts exist, what transactions need bookkeeping, which statements or invoices should be saved, and what recent activity deserves attention.
If you need setup first, start with [Connect your Mercury API token](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

Mercury stays read-only here by design. The skill can read Mercury data freely, and it can save exports or downloads to your machine only after an explicit local-file approval.

## A good first ask

"Check the Mercury skill is configured, list my accounts, and preview a CSV export of this month's transactions without writing any files yet."

## Good jobs to give the agent

- "List all my Mercury accounts and show the account IDs."
- "Export all transactions from January 1 to December 31 to a CSV for my accountant, but start with a dry-run plan."
- "Download statement PDFs for this account so I can reconcile monthly."
- "List invoices for this customer and download the PDF for invoice X."
- "Download this invoice attachment to my computer, but preview the file path first."
- "Pull the latest Mercury events so I can audit recent activity."
- "Show me treasury transactions for this treasury account."
- "Summarize recent transaction volume and totals by category."

## What it will not do

- approve payments
- send money
- edit customers, invoices, or webhooks
- change Mercury settings
- write anything back into Mercury

## What you should expect from the agent

For normal reads, the agent should fetch the data and explain it clearly.

For exports or downloads, the agent should:

1. show a dry-run preview first
2. wait for explicit approval before writing any local file
3. verify the file was written successfully
4. return a short receipt with the saved path and proof details
