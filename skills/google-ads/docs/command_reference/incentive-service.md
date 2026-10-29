# IncentiveService (Google Ads API v25)

Command shape:
- `google-ads-api-tool incentive-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `apply-incentive` — `IncentiveService.ApplyIncentive` (write; plan-first; unary_unary) — request: `ApplyIncentiveRequest` → response: `ApplyIncentiveResponse`
- `fetch-incentive` — `IncentiveService.FetchIncentive` (read; unary_unary) — request: `FetchIncentiveRequest` → response: `FetchIncentiveResponse`
