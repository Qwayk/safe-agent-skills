# AudienceInsightsService (Google Ads API v25)

Command shape:
- `google-ads-api-tool audience-insights-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-audience-composition-insights` — `AudienceInsightsService.GenerateAudienceCompositionInsights` (read; unary_unary) — request: `GenerateAudienceCompositionInsightsRequest` → response: `GenerateAudienceCompositionInsightsResponse`
- `generate-audience-definition` — `AudienceInsightsService.GenerateAudienceDefinition` (read; unary_unary) — request: `GenerateAudienceDefinitionRequest` → response: `GenerateAudienceDefinitionResponse`
- `generate-audience-overlap-insights` — `AudienceInsightsService.GenerateAudienceOverlapInsights` (read; unary_unary) — request: `GenerateAudienceOverlapInsightsRequest` → response: `GenerateAudienceOverlapInsightsResponse`
- `generate-insights-finder-report` — `AudienceInsightsService.GenerateInsightsFinderReport` (read; unary_unary) — request: `GenerateInsightsFinderReportRequest` → response: `GenerateInsightsFinderReportResponse`
- `generate-suggested-targeting-insights` — `AudienceInsightsService.GenerateSuggestedTargetingInsights` (read; unary_unary) — request: `GenerateSuggestedTargetingInsightsRequest` → response: `GenerateSuggestedTargetingInsightsResponse`
- `generate-targeting-suggestion-metrics` — `AudienceInsightsService.GenerateTargetingSuggestionMetrics` (read; unary_unary) — request: `GenerateTargetingSuggestionMetricsRequest` → response: `GenerateTargetingSuggestionMetricsResponse`
- `list-audience-insights-attributes` — `AudienceInsightsService.ListAudienceInsightsAttributes` (read; unary_unary) — request: `ListAudienceInsightsAttributesRequest` → response: `ListAudienceInsightsAttributesResponse`
- `list-insights-eligible-dates` — `AudienceInsightsService.ListInsightsEligibleDates` (read; unary_unary) — request: `ListInsightsEligibleDatesRequest` → response: `ListInsightsEligibleDatesResponse`
