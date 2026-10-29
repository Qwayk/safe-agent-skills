# ReachPlanService (Google Ads API v25)

Command shape:
- `google-ads-api-tool reach-plan-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-conversion-rates` — `ReachPlanService.GenerateConversionRates` (read; unary_unary) — request: `GenerateConversionRatesRequest` → response: `GenerateConversionRatesResponse`
- `generate-reach-forecast` — `ReachPlanService.GenerateReachForecast` (read; unary_unary) — request: `GenerateReachForecastRequest` → response: `GenerateReachForecastResponse`
- `list-plannable-locations` — `ReachPlanService.ListPlannableLocations` (read; unary_unary) — request: `ListPlannableLocationsRequest` → response: `ListPlannableLocationsResponse`
- `list-plannable-products` — `ReachPlanService.ListPlannableProducts` (read; unary_unary) — request: `ListPlannableProductsRequest` → response: `ListPlannableProductsResponse`
- `list-plannable-user-interests` — `ReachPlanService.ListPlannableUserInterests` (read; unary_unary) — request: `ListPlannableUserInterestsRequest` → response: `ListPlannableUserInterestsResponse`
- `list-plannable-user-lists` — `ReachPlanService.ListPlannableUserLists` (read; unary_unary) — request: `ListPlannableUserListsRequest` → response: `ListPlannableUserListsResponse`
