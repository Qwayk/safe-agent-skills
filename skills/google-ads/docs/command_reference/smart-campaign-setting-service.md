# SmartCampaignSettingService (Google Ads API v25)

Command shape:
- `google-ads-api-tool smart-campaign-setting-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `get-smart-campaign-status` — `SmartCampaignSettingService.GetSmartCampaignStatus` (read; unary_unary) — request: `GetSmartCampaignStatusRequest` → response: `GetSmartCampaignStatusResponse`
- `mutate-smart-campaign-settings` — `SmartCampaignSettingService.MutateSmartCampaignSettings` (write; plan-first; unary_unary) — request: `MutateSmartCampaignSettingsRequest` → response: `MutateSmartCampaignSettingsResponse`
