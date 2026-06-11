# How this skill stays safe

This skill is read-mostly today.

The safest starting point is a simple boards-and-pins snapshot before you plan any live account change.

## What stays simple

- inventory reads
- analytics reads
- ads reads
- catalog reads
- audit snapshots built from read-only Pinterest calls

Those flows do not send Pinterest writes.

## What needs extra care

Current remote write families are still plan-first because they do not have saved before-state support yet.

That means:

- the default path is a dry-run plan or read-only preview
- confirmed apply still needs `--apply --yes`
- destructive work can also need `--ack-irreversible`
- spend-sensitive work can also need `--ack-spend`
- high-volume or remote-work-triggering commands can also need `--ack-volume`
- no-snapshot paths also need explicit no-snapshot approval before live Pinterest HTTP

## What this skill does not promise

- no rollback
- no restore
- no provider backup
- no saved before-state for current live write families

The tool should say those limits plainly before any live Pinterest write is allowed.

## Local writes that are allowed

- `audit snapshot` can write JSON files locally after read-only Pinterest calls
- `pins links plan` can write a local plan file
- optional `--log-file` can write redacted JSONL audit events

## Local writes that still need no-snapshot approval

- `auth login`
- `auth code exchange`
- `auth token set`
- report outputs, receipts, or job output that only happen after a write path

Those flows can write token state or other local files without a saved before-state, so they still need explicit no-snapshot approval first.

## Write families that stay plan-first

- boards
- board sections
- pins
- pin-link apply
- ads campaign, ad-group, and ad writes
- catalog create and feed write flows
- ads report creation and run flows
- batch jobs that include remote-write rows

## Recommended workflow with an AI agent

1. Start with a small read or audit snapshot.
2. If you need a change, review the dry-run plan first.
3. Check whether the command needs irreversible, spend, volume, or no-snapshot approval.
4. Approve only when the target, payload, and limits are clear.
5. Save the plan, refusal, or receipt when you want an audit trail.
