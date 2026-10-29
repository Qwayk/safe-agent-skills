# ConversionAdjustmentUploadService (Google Ads API v25)

Command shape:
- `google-ads-api-tool conversion-adjustment-upload-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `upload-conversion-adjustments` — `ConversionAdjustmentUploadService.UploadConversionAdjustments` (write; plan-first; unary_unary) — request: `UploadConversionAdjustmentsRequest` → response: `UploadConversionAdjustmentsResponse`
