# OfflineUserDataJobService (Google Ads API v25)

Command shape:
- `google-ads-api-tool offline-user-data-job-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `add-offline-user-data-job-operations` — `OfflineUserDataJobService.AddOfflineUserDataJobOperations` (write; plan-first; unary_unary) — request: `AddOfflineUserDataJobOperationsRequest` → response: `AddOfflineUserDataJobOperationsResponse`
- `create-offline-user-data-job` — `OfflineUserDataJobService.CreateOfflineUserDataJob` (write; plan-first; unary_unary) — request: `CreateOfflineUserDataJobRequest` → response: `CreateOfflineUserDataJobResponse`
- `run-offline-user-data-job` — `OfflineUserDataJobService.RunOfflineUserDataJob` (write; plan-first; unary_unary) — request: `RunOfflineUserDataJobRequest` → response: `Operation`
