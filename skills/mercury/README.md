# Mercury

**Capability:** Read-only

Mercury is where business money questions become concrete: account balances, transactions, statements, invoices, recipients, treasury activity, and bookkeeping exports. This skill helps an agent review those records and prepare local exports or downloads without giving it any way to change Mercury itself.

It is useful for questions like "Which accounts do I have?", "Can you export this month of transactions for bookkeeping?", "Can you download these statements or invoices?", or "What recent Mercury events should I review?"

The tool is read-only against Mercury. It does not send money, approve payments, edit invoices, or change settings. The only writes it can do are local file exports or downloads on your own machine, and those start as dry-run plans before any file is written.

A good first ask is: "Check the Mercury skill is configured, list my accounts, and preview a transaction export for bookkeeping without writing any files yet."

## Start here first

- Want ideas for real Mercury work? [What you can do with Mercury](docs/use_cases.md)
- Need setup? [Connect your Mercury API token](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review Mercury accounts, balances, cards, transactions, users, and recipients.
- Export transaction history to JSON or CSV for bookkeeping or audits.
- Download statement PDFs, invoice PDFs, and invoice attachments to your machine.
- Check customers, invoices, webhooks, events, treasury activity, and journal entries.
- Run a transactions summary report without changing anything in Mercury.

## What access this skill needs

- A Mercury API token stored locally in your `.env` file.
- The right Mercury base URL for production or sandbox.
- A local output path when you want exports or downloads saved to your machine.

## Install and first run

Install slug: `mercury`

Ask your agent to install the `mercury` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@mercury -g -y
```

Then try a safe first ask like:

```text
Check the Mercury skill is configured, list my accounts, and preview a CSV export of this month's transactions without writing any files yet.
```

## How this skill stays safe

- It refuses all non-GET Mercury API requests.
- It never changes anything inside Mercury.
- Local exports and downloads start as dry-run plans first.
- Local file writes need `--apply`, and overwriting an existing file also needs `--yes`.
- Signed attachment URLs are treated as sensitive and redacted from outputs, plans, receipts, and logs.
- The docs, tests, examples, and API coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- organization, account, card, transaction, user, recipient, category, credit, and event reads
- customer, invoice, invoice-attachment, and statement reads
- treasury, webhook, and books journal-entry reads
- local transaction exports to JSON or CSV
- local downloads for invoices, statements, and invoice attachments
- a local transactions summary report

## What happens before a real change

This skill does not change Mercury itself.

When a task needs a local export or download:

- the agent should show the dry-run plan first
- you review the output path, filters, and file type
- the local write only happens after `--apply`
- overwriting an existing file also needs `--yes`
- after apply, the tool verifies the file exists and returns a receipt

## What proof it leaves behind

- Normal reads return machine-readable JSON you can save or review.
- Export and download plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Exports and downloads also write local run history under `.state/runs/`.
- The proof pack includes committed redacted examples, tests, and the API coverage ledger.

## Limits

- No Mercury creates, edits, deletes, approvals, or other non-GET remote actions.
- Real Mercury account work still needs a valid API token and the correct base URL.
- Exports and downloads write only to your local machine, not back into Mercury.
- Large exports can still pull more data than you meant to if you skip careful filters or page limits.

## Helpful docs

- [Browse all Mercury docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Jobs and batch guide](docs/jobs_and_batches.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
