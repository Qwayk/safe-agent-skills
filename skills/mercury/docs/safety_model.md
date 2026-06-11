# How this skill stays safe

Mercury access is intentionally read-only here.

## What this skill will never do

- create, edit, delete, approve, or send anything in Mercury
- turn `--apply` into a Mercury write
- print secrets into stdout, stderr, plans, receipts, or logs

## What this skill does safely

- read Mercury API v1 data through GET requests only
- refuse any non-GET Mercury request by design
- preview local exports and downloads before any file is written
- require `--apply` for local file writes
- require `--yes` before overwriting an existing file
- verify that a written file exists and is non-empty after apply
- redact signed download URLs from outputs, plans, receipts, and verbose logs

## The real risk to watch

The main risk is not a bad Mercury write, because this skill does not write to Mercury.

The real risks are:

- exporting the wrong date range or account
- downloading to the wrong path
- overwriting a file you wanted to keep
- exposing a sensitive attachment URL

## Recommended workflow with an AI agent

1. Run `auth check`.
2. Do one small read first so you know the account and scope look right.
3. If you need a local export or download, review the dry-run plan first.
4. Apply only after the path, filters, and file type look right.
5. Check the receipt or run history if you want an audit trail.

## Plans, receipts, and run history

For local exports and downloads, the dry-run output is the plan.

You can also save it explicitly with:

- `--plan-out <path>`

After apply, you can save the receipt with:

- `--receipt-out <path>`

Exports and downloads also create local run history under:

- `.state/runs/<run_id>/`
- `.state/runs/index.jsonl`

These files are local proof of what was reviewed, what was written, and how it was verified.

## Risk levels

- Low: normal Mercury reads
- Medium: writing a new local export or download file
- High: overwriting an existing local file

## Recovery story

There is no Mercury rollback story here because this skill does not change Mercury.

For local file writes, recovery is usually simple:

- keep the file if it is the result you wanted
- delete the file manually if it is not
