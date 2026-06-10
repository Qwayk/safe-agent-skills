# OfflineUserDataJobService (Google Ads API v22)

Command shape:
- `google-ads-api-tool offline-user-data-job-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `add-offline-user-data-job-operations` — `OfflineUserDataJobService.AddOfflineUserDataJobOperations` (read; unary) — request: `AddOfflineUserDataJobOperationsRequest` → response: `AddOfflineUserDataJobOperationsResponse`
- `create-offline-user-data-job` — `OfflineUserDataJobService.CreateOfflineUserDataJob` (write; unary) — request: `CreateOfflineUserDataJobRequest` → response: `CreateOfflineUserDataJobResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `run-offline-user-data-job` — `OfflineUserDataJobService.RunOfflineUserDataJob` (write; unary) — request: `RunOfflineUserDataJobRequest` → response: `Operation` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
