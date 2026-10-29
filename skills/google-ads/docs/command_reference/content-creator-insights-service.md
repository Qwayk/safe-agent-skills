# ContentCreatorInsightsService (Google Ads API v25)

Command shape:
- `google-ads-api-tool content-creator-insights-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-creator-insights` — `ContentCreatorInsightsService.GenerateCreatorInsights` (read; unary_unary) — request: `GenerateCreatorInsightsRequest` → response: `GenerateCreatorInsightsResponse`
- `generate-trending-insights` — `ContentCreatorInsightsService.GenerateTrendingInsights` (read; unary_unary) — request: `GenerateTrendingInsightsRequest` → response: `GenerateTrendingInsightsResponse`
