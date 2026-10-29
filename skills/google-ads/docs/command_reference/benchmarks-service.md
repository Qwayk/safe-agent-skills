# BenchmarksService (Google Ads API v25)

Command shape:
- `google-ads-api-tool benchmarks-service <method-kebab> --in request.json`

Notes:
- Requests are JSON objects matching the selected RPC request message. Unknown fields are rejected.
- Write methods are plan-first. Live apply requires the allowlist and applicable risk approvals; unsupported snapshot shapes remain blocked unless explicitly supported.

## Methods
- `generate-benchmarks-metrics` — `BenchmarksService.GenerateBenchmarksMetrics` (read; unary_unary) — request: `GenerateBenchmarksMetricsRequest` → response: `GenerateBenchmarksMetricsResponse`
- `list-benchmarks-available-dates` — `BenchmarksService.ListBenchmarksAvailableDates` (read; unary_unary) — request: `ListBenchmarksAvailableDatesRequest` → response: `ListBenchmarksAvailableDatesResponse`
- `list-benchmarks-locations` — `BenchmarksService.ListBenchmarksLocations` (read; unary_unary) — request: `ListBenchmarksLocationsRequest` → response: `ListBenchmarksLocationsResponse`
- `list-benchmarks-products` — `BenchmarksService.ListBenchmarksProducts` (read; unary_unary) — request: `ListBenchmarksProductsRequest` → response: `ListBenchmarksProductsResponse`
- `list-benchmarks-sources` — `BenchmarksService.ListBenchmarksSources` (read; unary_unary) — request: `ListBenchmarksSourcesRequest` → response: `ListBenchmarksSourcesResponse`
