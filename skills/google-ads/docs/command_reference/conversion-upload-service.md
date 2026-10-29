# ConversionUploadService (Google Ads API v25)

Command shape:
- `google-ads-api-tool conversion-upload-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `upload-call-conversions` — `ConversionUploadService.UploadCallConversions` (write; plan-first; unary_unary) — request: `UploadCallConversionsRequest` → response: `UploadCallConversionsResponse`
- `upload-click-conversions` — `ConversionUploadService.UploadClickConversions` (write; plan-first; unary_unary) — request: `UploadClickConversionsRequest` → response: `UploadClickConversionsResponse`
