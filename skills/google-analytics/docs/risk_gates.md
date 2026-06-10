# Risk gates (GA4)

This tool is safe-by-default:

- Read-like GA4 methods execute directly.
- Write-like GA4 methods are **dry-run by default**.

For write-like methods, the tool will:

- build a deterministic **plan** (safe, redacted)
- refuse unsafe applies unless the right flags + reviewed plan are present
- after the gates pass: require explicit no-snapshot approval before GA4 HTTP until safe before-state capture exists

## Risk levels

The tool classifies each discovery method into a risk level:

- `low`: HTTP `GET` plus an explicit allowlist of read-like `POST` methods (reports/search)
- `medium`: other `POST`/`PUT`/`PATCH`
- `high`: batch writes, access-control changes, or clearly risky “provisioning” methods
- `irreversible`: HTTP `DELETE`

## Apply gates

These gates are enforced **before any network call**:

- `low` apply:
  - `--apply`
  - `--plan-in` optional (if provided, drift-checked)
- `medium` apply:
  - `--apply`
  - `--plan-in` optional (if provided, drift-checked)
- `high` apply:
  - `--apply --yes --plan-in <file>`
- `irreversible` apply:
  - `--apply --yes --ack-irreversible --plan-in <file>`

After these gates and any plan drift checks pass, current write-like apply requests still require explicit no-snapshot approval before GA4 HTTP. No provider write is sent and no receipt is created.

## Read-like POST allowlist

These `POST` methods are treated as `low` risk because they are report/search style:

- Data API: `runReport`, `runPivotReport`, `runRealtimeReport`, `batchRunReports`, `batchRunPivotReports`, `checkCompatibility`, `runFunnelReport`, `audienceExports.query`
- Admin API: `runAccessReport`, `searchChangeHistoryEvents`

## High-risk rules (examples)

These are treated as `high` risk:

- any method under `*.accessBindings.*` (permission changes)
- batch write helpers (method name starts with `batch`, except report batch methods)
- account provisioning (`provisionAccountTicket`)
