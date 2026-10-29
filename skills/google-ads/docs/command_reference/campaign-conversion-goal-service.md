# CampaignConversionGoalService (Google Ads API v25)

Command shape:
- `google-ads-api-tool campaign-conversion-goal-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `mutate-campaign-conversion-goals` — `CampaignConversionGoalService.MutateCampaignConversionGoals` (write; plan-first; unary_unary) — request: `MutateCampaignConversionGoalsRequest` → response: `MutateCampaignConversionGoalsResponse`
