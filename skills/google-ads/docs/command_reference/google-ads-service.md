# GoogleAdsService (Google Ads API v25)

Command shape:
- `google-ads-api-tool google-ads-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate` — `GoogleAdsService.Mutate` (write; plan-first; unary_unary) — request: `MutateGoogleAdsRequest` → response: `MutateGoogleAdsResponse`
- `search` — `GoogleAdsService.Search` (read; unary_unary) — request: `SearchGoogleAdsRequest` → response: `SearchGoogleAdsResponse`
- `search-stream` — `GoogleAdsService.SearchStream` (read; unary_stream) — request: `SearchGoogleAdsStreamRequest` → response: `SearchGoogleAdsStreamResponse`
