# GoogleAdsFieldService (Google Ads API v22)

Command shape:
- `google-ads-api-tool google-ads-field-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `get-google-ads-field` — `GoogleAdsFieldService.GetGoogleAdsField` (read; unary) — request: `GetGoogleAdsFieldRequest` → response: `GoogleAdsField`
- `search-google-ads-fields` — `GoogleAdsFieldService.SearchGoogleAdsFields` (read; unary) — request: `SearchGoogleAdsFieldsRequest` → response: `SearchGoogleAdsFieldsResponse`
