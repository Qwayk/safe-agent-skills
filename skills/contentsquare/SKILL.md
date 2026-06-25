---
name: contentsquare-safe-cli
description: Use the local Contentsquare Safe CLI for server-side Data Export, Metrics, Enrichment, and Speed Analysis Lab work with safe dry-run/review/apply gates.
---

# Contentsquare Safe CLI

Trigger this skill when the user wants help with Contentsquare Data Export, metrics, enrichment batches, Speed Analysis Lab reports, or a reviewed server-side Contentsquare change.

Start with a safe read. A good first move is to check Contentsquare access, name the API endpoint the token uses, run one small read the user can recognize, explain the result in normal words, and stop before any live change.

## First checks

1. Run `contentsquare-safe-cli onboarding` when setup may be missing.
2. Run `contentsquare-safe-cli auth check` before live reads.
3. Never ask the user to paste `CONTENTSQUARE_CLIENT_SECRET` or access tokens into chat.

OAuth scopes are chosen by command family. Use the default family scopes unless the user or project docs explicitly require an official override. For account-level OAuth credentials, use `CONTENTSQUARE_PROJECT_ID` in `.env` or pass `--oauth-project-id` before the command.

## Safe reads

Use read commands directly for Data Export reads, Metrics reads, and Speed Analysis report/list endpoints.

Good first commands:

- `contentsquare-safe-cli data-export list-jobs --state completed --limit 25`
- `contentsquare-safe-cli metrics site bounce-rate --project-id <id> --start-date <date> --end-date <date>`
- `contentsquare-safe-cli speed-analysis monitoring-list --body-json body.json`

When using filters, keep the CLI flags readable. The tool sends official Contentsquare query names to the API, such as `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `period`, `ids`, `state`, `order`, `format`, `frequency`, `scope`, `from`, and `to`.

## Live changes

Never apply a live change first.

1. Create a dry-run plan with `--plan-out`.
2. Review the plan against the user's goal.
3. Apply only with `--plan-in --apply --yes`.
4. Add `--ack-no-snapshot` for Enrichment sends and Speed Analysis event writes.
5. Add `--ack-irreversible` for Speed Analysis event deletes.
6. Save a receipt with `--receipt-out` when applying.

## Reporting back

Tell the user what happened in plain English:

- risk level
- whether anything changed
- how it was verified
- where proof was saved

Do not print secrets, tokens, raw auth responses, or `.env` contents.
