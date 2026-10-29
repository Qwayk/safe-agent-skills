# AdGroupAdService (Google Ads API v25)

Command shape:
- `google-ads-api-tool ad-group-ad-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate-ad-group-ads` — `AdGroupAdService.MutateAdGroupAds` (write; plan-first; unary_unary) — request: `MutateAdGroupAdsRequest` → response: `MutateAdGroupAdsResponse`
- `remove-automatically-created-assets` — `AdGroupAdService.RemoveAutomaticallyCreatedAssets` (write; plan-first; unary_unary) — request: `RemoveAutomaticallyCreatedAssetsRequest` → response: `Empty`
