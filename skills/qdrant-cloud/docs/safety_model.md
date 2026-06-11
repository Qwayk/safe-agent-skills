# How this skill stays safe

This skill is careful by default.

The safest first step is a simple live inventory read like account, cluster, or backup review before you plan any change.

## What stays simple

- offline config checks
- live account reads
- live cluster and backup reads
- live billing, IAM, and monitoring reads

Those flows still need the right API key, but they do not change Qdrant Cloud resources.

## What needs extra care

Current ordinary writes are still plan-first because many operations do not have saved before-state or provider backup capture yet.

That means:

- nothing reaches the real API unless you add `--live`
- the default path for a write is a dry-run plan
- confirmed apply needs `--live --apply`
- higher-risk work can also need `--yes`
- destructive work can also need `--ack-irreversible`
- billing or payment work can also need `--ack-spend-money`
- ordinary writes without saved before-state or provider backup also need explicit no-snapshot approval before Qdrant Cloud HTTP

## What this skill does not promise

- no generic rollback
- no hidden network calls
- no automatic restore for ordinary writes
- no saved before-state for every write family

The tool should say those limits plainly before any live write is allowed.

## The narrow recovery exception

These workflows are different because they are already explicit provider recovery paths:

- `create-backup`
- `restore-backup`
- `create-cluster-from-backup`

They still need the normal gates, but they are not the same as pretending a normal write has automatic rollback.

## Local files and proof

This skill can save:

- dry-run plans with `--plan-out`
- provider backup or restore receipts with `--receipt-out`
- local run history under `.state/runs`

Those files are meant to help review what happened later. They must not contain secrets.

## Recommended workflow with an AI agent

1. Start with a live read that proves the account and target IDs are correct.
2. If you need a change, review the dry-run plan first.
3. Check whether the action also needs destructive, spend, or no-snapshot approval.
4. Keep provider backup and restore workflows separate from ordinary writes.
5. Save the plan, refusal, or receipt when you want an audit trail.
