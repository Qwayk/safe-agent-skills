# ReachPlanService (Google Ads API v22)

Command shape:
- `google-ads-api-tool reach-plan-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects that map to the RPC request message for the chosen method.
- Unknown fields are rejected (strict JSON→protobuf parsing).
- Write methods are plan-first by default; add `--apply` only after explicit approval (see `docs/safety_model.md`).

## Methods
- `generate-conversion-rates` — `ReachPlanService.GenerateConversionRates` (read; unary) — request: `GenerateConversionRatesRequest` → response: `GenerateConversionRatesResponse`
- `generate-reach-forecast` — `ReachPlanService.GenerateReachForecast` (read; unary) — request: `GenerateReachForecastRequest` → response: `GenerateReachForecastResponse`
- `list-plannable-locations` — `ReachPlanService.ListPlannableLocations` (read; unary) — request: `ListPlannableLocationsRequest` → response: `ListPlannableLocationsResponse`
- `list-plannable-products` — `ReachPlanService.ListPlannableProducts` (read; unary) — request: `ListPlannableProductsRequest` → response: `ListPlannableProductsResponse`
- `list-plannable-user-interests` — `ReachPlanService.ListPlannableUserInterests` (read; unary) — request: `ListPlannableUserInterestsRequest` → response: `ListPlannableUserInterestsResponse`
- `list-plannable-user-lists` — `ReachPlanService.ListPlannableUserLists` (read; unary) — request: `ListPlannableUserListsRequest` → response: `ListPlannableUserListsResponse`
