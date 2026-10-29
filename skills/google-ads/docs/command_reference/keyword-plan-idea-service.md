# KeywordPlanIdeaService (Google Ads API v25)

Command shape:
- `google-ads-api-tool keyword-plan-idea-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-ad-group-themes` — `KeywordPlanIdeaService.GenerateAdGroupThemes` (read; unary_unary) — request: `GenerateAdGroupThemesRequest` → response: `GenerateAdGroupThemesResponse`
- `generate-keyword-forecast-metrics` — `KeywordPlanIdeaService.GenerateKeywordForecastMetrics` (read; unary_unary) — request: `GenerateKeywordForecastMetricsRequest` → response: `GenerateKeywordForecastMetricsResponse`
- `generate-keyword-historical-metrics` — `KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics` (read; unary_unary) — request: `GenerateKeywordHistoricalMetricsRequest` → response: `GenerateKeywordHistoricalMetricsResponse`
- `generate-keyword-ideas` — `KeywordPlanIdeaService.GenerateKeywordIdeas` (read; unary_unary) — request: `GenerateKeywordIdeasRequest` → response: `GenerateKeywordIdeaResponse`
