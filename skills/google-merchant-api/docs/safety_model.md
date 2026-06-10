# Safety model

This tool keeps Merchant API work explicit, reviewable, and auditable.

## Core rules

- reads can run directly
- writes stay dry-run by default
- provider writes require explicit no-snapshot approval when no saved snapshot is available
- high-risk and irreversible applies require a reviewed `--plan-in`
- irreversible applies also require `--ack-irreversible`
- plans, refusals, receipts, and logs must stay secret-safe

## Risk levels

- `read`: read-only calls and read-like `POST` search/render calls
- `medium`: ordinary single-resource writes
- `high`: batch-style writes and status-change style writes such as `approve`, `reject`, `enable`, `disable`, `manage`, or `applyOrderUpdate`
- `irreversible`: `DELETE` operations

## Normal write flow

1. Run the command without `--apply` and review the plan.
2. Save the plan with `--plan-out <file>` when another reviewer needs a stable copy.
3. The plan marks `before_state.required: true` and `before_state.supported: false`.
4. If `--apply` is attempted without required no-snapshot approval, the tool refuses before credentials or provider HTTP and reports that no Google Merchant write was sent.
5. With required approval, supported writes may proceed and the receipt must record the no-snapshot approval and recovery limits.

## Required apply flags

- medium write: `--apply`
- high-risk write: `--apply --yes --plan-in reviewed-plan.json`
- irreversible write: `--apply --yes --plan-in reviewed-plan.json --ack-irreversible`

## What the tool verifies

- the planned request shape matches on apply:
  - environment fingerprint
  - family
  - method id
  - HTTP method
  - path
  - query
  - body
  - risk level
- missing-approval write attempts stop before any live call
- approved write attempts record the explicit no-snapshot approval in the receipt

## Current verification limit

This tool does not yet auto-capture before-state or auto-generate a follow-up read for every Merchant method. Approved writes must disclose that limit and record explicit no-snapshot approval in the receipt. Matching read/list/get commands should be used after writes for stronger proof.
