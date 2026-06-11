# CampaignCriterionService (Google Ads API v22)

Command shape:
- `google-ads-api-tool campaign-criterion-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `mutate-campaign-criteria` — `CampaignCriterionService.MutateCampaignCriteria` (write; unary) — request: `MutateCampaignCriteriaRequest` → response: `MutateCampaignCriteriaResponse` (plan-first; supported update applies and readable ad-schedule removes save before-state when possible; other non-update live apply needs explicit no-snapshot approval support or a true blocker reason; allowlist required)
