# GoogleAdsFieldService (Google Ads API v25)

Command shape:
- `google-ads-api-tool google-ads-field-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `get-google-ads-field` — `GoogleAdsFieldService.GetGoogleAdsField` (read; unary_unary) — request: `GetGoogleAdsFieldRequest` → response: `GoogleAdsField`
- `search-google-ads-fields` — `GoogleAdsFieldService.SearchGoogleAdsFields` (read; unary_unary) — request: `SearchGoogleAdsFieldsRequest` → response: `SearchGoogleAdsFieldsResponse`
