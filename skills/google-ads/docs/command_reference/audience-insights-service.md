# AudienceInsightsService (Google Ads API v22)

Command shape:
- `google-ads-api-tool audience-insights-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `generate-audience-composition-insights` — `AudienceInsightsService.GenerateAudienceCompositionInsights` (read; unary) — request: `GenerateAudienceCompositionInsightsRequest` → response: `GenerateAudienceCompositionInsightsResponse`
- `generate-audience-overlap-insights` — `AudienceInsightsService.GenerateAudienceOverlapInsights` (read; unary) — request: `GenerateAudienceOverlapInsightsRequest` → response: `GenerateAudienceOverlapInsightsResponse`
- `generate-insights-finder-report` — `AudienceInsightsService.GenerateInsightsFinderReport` (read; unary) — request: `GenerateInsightsFinderReportRequest` → response: `GenerateInsightsFinderReportResponse`
- `generate-suggested-targeting-insights` — `AudienceInsightsService.GenerateSuggestedTargetingInsights` (read; unary) — request: `GenerateSuggestedTargetingInsightsRequest` → response: `GenerateSuggestedTargetingInsightsResponse`
- `generate-targeting-suggestion-metrics` — `AudienceInsightsService.GenerateTargetingSuggestionMetrics` (read; unary) — request: `GenerateTargetingSuggestionMetricsRequest` → response: `GenerateTargetingSuggestionMetricsResponse`
- `list-audience-insights-attributes` — `AudienceInsightsService.ListAudienceInsightsAttributes` (read; unary) — request: `ListAudienceInsightsAttributesRequest` → response: `ListAudienceInsightsAttributesResponse`
- `list-insights-eligible-dates` — `AudienceInsightsService.ListInsightsEligibleDates` (read; unary) — request: `ListInsightsEligibleDatesRequest` → response: `ListInsightsEligibleDatesResponse`
