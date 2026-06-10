# BatchJobService (Google Ads API v22)

Command shape:
- `google-ads-api-tool batch-job-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `add-batch-job-operations` — `BatchJobService.AddBatchJobOperations` (read; unary) — request: `AddBatchJobOperationsRequest` → response: `AddBatchJobOperationsResponse`
- `list-batch-job-results` — `BatchJobService.ListBatchJobResults` (read; unary) — request: `ListBatchJobResultsRequest` → response: `ListBatchJobResultsResponse`
- `mutate-batch-job` — `BatchJobService.MutateBatchJob` (write; unary) — request: `MutateBatchJobRequest` → response: `MutateBatchJobResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
- `run-batch-job` — `BatchJobService.RunBatchJob` (write; unary) — request: `RunBatchJobRequest` → response: `Operation` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
