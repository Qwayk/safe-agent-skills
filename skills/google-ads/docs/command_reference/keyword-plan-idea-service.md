# KeywordPlanIdeaService (Google Ads API v22)

Command shape:
- `google-ads-api-tool keyword-plan-idea-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `generate-ad-group-themes` — `KeywordPlanIdeaService.GenerateAdGroupThemes` (read; unary) — request: `GenerateAdGroupThemesRequest` → response: `GenerateAdGroupThemesResponse`
- `generate-keyword-forecast-metrics` — `KeywordPlanIdeaService.GenerateKeywordForecastMetrics` (read; unary) — request: `GenerateKeywordForecastMetricsRequest` → response: `GenerateKeywordForecastMetricsResponse`
- `generate-keyword-historical-metrics` — `KeywordPlanIdeaService.GenerateKeywordHistoricalMetrics` (read; unary) — request: `GenerateKeywordHistoricalMetricsRequest` → response: `GenerateKeywordHistoricalMetricsResponse`
- `generate-keyword-ideas` — `KeywordPlanIdeaService.GenerateKeywordIdeas` (read; unary) — request: `GenerateKeywordIdeasRequest` → response: `GenerateKeywordIdeaResponse`
