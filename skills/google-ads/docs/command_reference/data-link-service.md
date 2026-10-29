# DataLinkService (Google Ads API v25)

Command shape:
- `google-ads-api-tool data-link-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `create-data-link` — `DataLinkService.CreateDataLink` (write; plan-first; unary_unary) — request: `CreateDataLinkRequest` → response: `CreateDataLinkResponse`
- `remove-data-link` — `DataLinkService.RemoveDataLink` (write; plan-first; unary_unary) — request: `RemoveDataLinkRequest` → response: `RemoveDataLinkResponse`
- `update-data-link` — `DataLinkService.UpdateDataLink` (write; plan-first; unary_unary) — request: `UpdateDataLinkRequest` → response: `UpdateDataLinkResponse`
