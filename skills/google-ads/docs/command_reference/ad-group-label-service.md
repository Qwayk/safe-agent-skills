# AdGroupLabelService (Google Ads API v25)

Command shape:
- `google-ads-api-tool ad-group-label-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate-ad-group-labels` — `AdGroupLabelService.MutateAdGroupLabels` (write; plan-first; unary_unary) — request: `MutateAdGroupLabelsRequest` → response: `MutateAdGroupLabelsResponse`
