# GeoTargetConstantService (Google Ads API v25)

Command shape:
- `google-ads-api-tool geo-target-constant-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `suggest-geo-target-constants` — `GeoTargetConstantService.SuggestGeoTargetConstants` (read; unary_unary) — request: `SuggestGeoTargetConstantsRequest` → response: `SuggestGeoTargetConstantsResponse`
