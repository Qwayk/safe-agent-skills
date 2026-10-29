# BatchJobService (Google Ads API v25)

Command shape:
- `google-ads-api-tool batch-job-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `add-batch-job-operations` — `BatchJobService.AddBatchJobOperations` (write; plan-first; unary_unary) — request: `AddBatchJobOperationsRequest` → response: `AddBatchJobOperationsResponse`
- `list-batch-job-results` — `BatchJobService.ListBatchJobResults` (read; unary_unary) — request: `ListBatchJobResultsRequest` → response: `ListBatchJobResultsResponse`
- `mutate-batch-job` — `BatchJobService.MutateBatchJob` (write; plan-first; unary_unary) — request: `MutateBatchJobRequest` → response: `MutateBatchJobResponse`
- `run-batch-job` — `BatchJobService.RunBatchJob` (write; plan-first; unary_unary) — request: `RunBatchJobRequest` → response: `Operation`
