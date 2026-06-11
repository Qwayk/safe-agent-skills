# Safety model

## Reads

- Read commands run immediately.
- Paginated reads can use `--all` with a page guardrail.

## Writes

- Writes never apply by default.
- A write without `--apply` returns a dry-run plan.
- The plan explicitly declares: no WooCommerce snapshots, no provider backups, and no machine rollback plans are created.
- Write plans include `before_state.required: true`, `before_state.supported: false`, and a `no-snapshot-approval` verification plan.
- Apply requests use `--apply --plan-in plan.json`.
- High-risk writes also need `--yes`.
- After required flags and plan drift checks pass, write apply saves before-state when practical. When no useful before-state can be saved, apply requires explicit no-snapshot approval before WooCommerce HTTP and records that limit in the receipt.

High-risk writes include:

- delete commands
- batch endpoints
- order email actions
- payment gateway updates
- webhook writes
- shipping zone location updates
- system status tool runs

## Recovery contract

Write-capable commands save local proof files under `.state/runs/` unless `--no-artifacts` is used.
That gives you a plan, audit log, and run summary you can review later.
The tool does not provide automatic recovery. Approved supported write apply produces a receipt; missing approval or another safety blocker produces a safe refusal, and no WooCommerce write is sent in that refusal case.
