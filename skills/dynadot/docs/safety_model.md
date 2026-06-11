# Safety model

This skill is designed for high-volume Dynadot work where a mistake can affect many domains at once.

## What it protects you from

- pushing domains to the wrong Dynadot account
- changing name servers across a large list without review
- running monetary or irreversible actions too quickly
- leaking secrets like API keys in URLs or transfer auth codes in chat

## Before live changes

- Dry-run by default; no writes unless `--apply`.
- Most writes also require `--yes` and a reviewed `--plan-in`.
- Monetary or irreversible actions also require `--ack-irreversible`.
- Dynadot writes without a real saved before-state also require `--ack-no-snapshot`.
- Refuse when the target is unclear or the approval is missing.
- Never log secrets.

## Why no-snapshot approval matters here

Dynadot API3 is command-based, and many write commands do not give this tool a clean way to save a real before-state first.

That means:

- the tool can still preview the job honestly
- the tool can still verify parts of the result after apply
- but that read-back is not the same as a restore point

So write plans must say that clearly and ask for explicit no-snapshot approval before the live provider call.

## What verification means in this tool

Verification here means checking that the result looks right after the approved change.

Examples:

- name server changes can use read-back verification
- receiver-side transfer checks can confirm that domains arrived
- bulk receipts can show which rows ran and which failed

Those checks are useful proof, but they are not automatic rollback.

## Recovery contract

All current Dynadot write families in this CLI are `irreversible_and_clearly_labeled`.

That means:

- `recovery.end_state` is `irreversible_and_clearly_labeled`
- write plans include `recovery`
- `recovery.backups` is `[]`
- `recovery.snapshots` is `[]`
- `recovery.rollback_plan` is `null`
- approved supported writes create receipts that record the no-snapshot approval and recovery limit

## Plans, receipts, and refusals

For write-capable commands, treat the dry-run output as the plan:

- what will change
- what must be true before apply
- whether the command needs no-snapshot approval
- what proof the command can leave behind

When apply is attempted with the required gates, the command should leave one of two honest outcomes:

- a receipt for an approved supported write
- a safe refusal that says why the write stopped before Dynadot HTTP

## Safe resume for large runs

Some write commands can plan from an older receipt with `--resume-from-receipt <receipt.json>`.

That lets the tool:

- skip items already completed in an earlier run
- record the resume receipt hash in the new plan
- keep the same no-snapshot approval rule for the remaining live writes

## Proof files

The most useful file outputs are:

- `--plan-out <path>` for the dry-run plan
- `--plan-in <path>` when you apply from a reviewed plan
- `--receipt-out <path>` for the approved apply receipt

Run history also goes under `.state/runs/` next to your env file so you can review older runs later.
