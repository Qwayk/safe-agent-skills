# Safety model

`figma-safe-agent-cli` is safe-by-default for this Figma slice.

## Core rules

- Read operations immediately.
- Write operations produce a dry-run plan unless `--apply` is passed.
- Risky writes require `--yes` and, when flagged, `--ack-irreversible`.
- Plan-based apply is validated with `--plan-in` by checking request drift.
- Current write applies require explicit no-snapshot approval before Figma token use or provider HTTP when no saved snapshot is available.
- No secrets are written to stdout, files, or logs.

## Current write model

- Explicit operation commands (`operations <area> <op_key>`) default to preview for write methods (`POST`, `PUT`, `DELETE`) unless `--apply` is passed.
- `--plan-out` saves the plan.
- `--plan-in` is validated before the no-snapshot approval gate; mismatch blocks execution first.
- `--receipt-out` stores apply results for successful reviewed writes.
- `runs list/show` lets you inspect prior attempts.

## Verification reality

Current write verification is the provider response plus best-effort read-back when the operation supports it. Older helpers still remain best-effort, not rollback.
Read operations still use the response as the verification signal.

## Why the tool refuses

The tool returns a blocked/failure result with `ok: false` when:
- required auth is missing
- live `/v1/me` probe fails
- `--plan-in` replay does not match the built request
- path/query parsing is malformed

The tool returns a safe refusal with `ok: true` and `refused: true` when:
- a write is asked to apply without the required safety flags like `--yes`, `--ack-irreversible`, or `--ack-no-snapshot`
- a plan replay does not match the reviewed request

## For safe agent use

An agent should always:
1. run read-only checks first,
2. present the plan output,
3. wait for explicit approval,
4. try apply with required flags only when approved,
5. report the no-snapshot approval requirement or the saved receipt clearly for current writes.
