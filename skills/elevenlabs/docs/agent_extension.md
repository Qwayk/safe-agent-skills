# Agent extension guide

Extend the tool only when the provider operation and its safety boundary are explicit.

## Read or HTTP operation

1. Confirm the operation exists in `openapi.json` or add a deliberate manual row for a non-HTTP interface.
2. Regenerate the inventory and command reference.
3. Register a named command with explicit selectors and request fields.
4. Keep JSON mode to one JSON object and add offline shape tests.
5. Mark account, plan, fixture, and live-verification limits in the coverage and proof docs.

The generated boundary currently contains 388 HTTP operations (367 stable implemented, 21 deprecated), plus seven manual WebSocket surfaces (six plan-only commands and one callback-only reverse connection), one callback-only Twilio webhook, and one docs-only authentication row.

## Write operation

Keep the sequence plan → review → apply → verify → receipt. Dry-run is the default. Require `--live --apply`, plus `--ack-spend-money`, `--ack-irreversible`, or `--yes` when the operation requires them. If no real before-state can be captured, require `--ack-no-snapshot`; record `before_state.status: no_snapshot_available` and the recovery limit. Do not promise automatic rollback or live success.

## Non-HTTP rows

WebSockets and callbacks are documentation/extension boundaries, not generic HTTP commands. Their official sources and integration assumptions belong in [references](references.md); do not present them as verified local CLI operations.
