# ConversionAdjustmentUploadService (Google Ads API v22)

Command shape:
- `google-ads-api-tool conversion-adjustment-upload-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `upload-conversion-adjustments` — `ConversionAdjustmentUploadService.UploadConversionAdjustments` (write; unary) — request: `UploadConversionAdjustmentsRequest` → response: `UploadConversionAdjustmentsResponse` (plan-first; snapshot-backed live applies save before-state when possible; other write shapes need explicit no-snapshot approval support or a true blocker reason; allowlist required)
