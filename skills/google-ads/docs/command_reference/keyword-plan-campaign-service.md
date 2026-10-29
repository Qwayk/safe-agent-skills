# KeywordPlanCampaignService (Google Ads API v25)

Command shape:
- `google-ads-api-tool keyword-plan-campaign-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate-keyword-plan-campaigns` — `KeywordPlanCampaignService.MutateKeywordPlanCampaigns` (write; plan-first; unary_unary) — request: `MutateKeywordPlanCampaignsRequest` → response: `MutateKeywordPlanCampaignsResponse`
