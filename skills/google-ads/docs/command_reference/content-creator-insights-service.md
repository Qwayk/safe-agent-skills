# ContentCreatorInsightsService (Google Ads API v22)

Command shape:
- `google-ads-api-tool content-creator-insights-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `generate-creator-insights` — `ContentCreatorInsightsService.GenerateCreatorInsights` (read; unary) — request: `GenerateCreatorInsightsRequest` → response: `GenerateCreatorInsightsResponse`
- `generate-trending-insights` — `ContentCreatorInsightsService.GenerateTrendingInsights` (read; unary) — request: `GenerateTrendingInsightsRequest` → response: `GenerateTrendingInsightsResponse`
