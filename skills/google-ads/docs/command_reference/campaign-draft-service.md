# CampaignDraftService (Google Ads API v25)

Command shape:
- `google-ads-api-tool campaign-draft-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `list-campaign-draft-async-errors` — `CampaignDraftService.ListCampaignDraftAsyncErrors` (read; unary_unary) — request: `ListCampaignDraftAsyncErrorsRequest` → response: `ListCampaignDraftAsyncErrorsResponse`
- `mutate-campaign-drafts` — `CampaignDraftService.MutateCampaignDrafts` (write; plan-first; unary_unary) — request: `MutateCampaignDraftsRequest` → response: `MutateCampaignDraftsResponse`
- `promote-campaign-draft` — `CampaignDraftService.PromoteCampaignDraft` (write; plan-first; unary_unary) — request: `PromoteCampaignDraftRequest` → response: `Operation`
