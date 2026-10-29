# SmartCampaignSuggestService (Google Ads API v25)

Command shape:
- `google-ads-api-tool smart-campaign-suggest-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `suggest-keyword-themes` — `SmartCampaignSuggestService.SuggestKeywordThemes` (read; unary_unary) — request: `SuggestKeywordThemesRequest` → response: `SuggestKeywordThemesResponse`
- `suggest-smart-campaign-ad` — `SmartCampaignSuggestService.SuggestSmartCampaignAd` (read; unary_unary) — request: `SuggestSmartCampaignAdRequest` → response: `SuggestSmartCampaignAdResponse`
- `suggest-smart-campaign-budget-options` — `SmartCampaignSuggestService.SuggestSmartCampaignBudgetOptions` (read; unary_unary) — request: `SuggestSmartCampaignBudgetOptionsRequest` → response: `SuggestSmartCampaignBudgetOptionsResponse`
