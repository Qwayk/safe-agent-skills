# Workers Observability Telemetry endpoint coverage (detailed)

This file exists because Workers Observability “stored logs” operations are **sensitive** (may include PII/content) and should be called via the named `cloudflare-api-tool workers logs ...` commands (file-only output; never printed).

Note: The current vendored snapshot and CLI both use the account-scoped telemetry endpoints under `/accounts/{account_id}/workers/observability/telemetry/*`.

Implementation note: the first-class `cloudflare-api-tool workers logs ...` commands remain the preferred UX, and the explicit allowlisted operations surface for these same endpoints currently resolves through `accounts_writes`.

Legend:
- Implemented: runnable via the named `cloudflare-api-tool workers logs ...` commands and treated as sensitive file-only output (never printed).

| Status | Method | Path | OperationId | Summary | Tags | API token groups | CLI command(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| Implemented | POST | `/telemetry/keys` | `telemetry.keys.list` | List keys | Keys |  | cloudflare-api-tool operations workers_observability_telemetry telemetry-keys-list | Sensitive read (keys can reveal the event data model). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
| Implemented | POST | `/telemetry/values` | `telemetry.values.list` | List values | Values |  | cloudflare-api-tool operations workers_observability_telemetry telemetry-values-list | Sensitive read (values may include PII). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
| Implemented | POST | `/telemetry/query` | `telemetry.query` | Run a query | Query run |  | cloudflare-api-tool operations workers_observability_telemetry telemetry-query | Sensitive read (stored logs/events; may include PII). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
| Implemented | POST | `/accounts/{account_id}/workers/observability/telemetry/keys` | `telemetry.keys.list` | List keys | Keys | Workers Observability Write | cloudflare-api-tool operations accounts_writes telemetry-keys-list | Sensitive read (keys can reveal the event data model). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
| Implemented | POST | `/accounts/{account_id}/workers/observability/telemetry/values` | `telemetry.values.list` | List values | Values | Workers Observability Write | cloudflare-api-tool operations accounts_writes telemetry-values-list | Sensitive read (values may include PII). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
| Implemented | POST | `/accounts/{account_id}/workers/observability/telemetry/query` | `telemetry.query` | Run a query | Query run | Workers Observability Write | cloudflare-api-tool operations accounts_writes telemetry-query | Sensitive read (stored logs/events; may include PII). Requires `--apply` and `--out`; file-only output (never printed). Read-like POST (`changed=false`). |
