# AssetService (Google Ads API v25)

Command shape:
- `google-ads-api-tool asset-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate-assets` — `AssetService.MutateAssets` (write; plan-first; unary_unary) — request: `MutateAssetsRequest` → response: `MutateAssetsResponse`
