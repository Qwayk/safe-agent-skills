# API coverage

Contentsquare coverage shows exactly what the shipped commands can do: which official server-side REST endpoints have explicit commands, which areas are excluded from this product shape, and which safety class applies before a live change. If an endpoint or workflow is not listed here, do not assume the skill supports it.

This is source coverage, not live account proof. It shows which official Contentsquare operations the tool maps, how those operations are classified for safety, and which documented limits the user should preserve.

A good first coverage check is: search for the Contentsquare area you plan to use, then confirm the row has the expected method, endpoint, command, safety class, and documented limit before asking for a live read or plan.

Last verified against official Contentsquare docs: **2026-06-25**.

## Summary

| Area | Status | Count | Notes |
|---|---:|---:|---|
| OAuth | Shipped | 2 | Token requests use documented scopes and optional account-level `project_id`; credential identity uses the documented body |
| Data Export | Shipped | 9 | Job creation is plan-first |
| Metrics | Shipped | 59 | One all-zone path appears in both Web and Apps docs and is counted honestly as two docs rows |
| Enrichment | Shipped | 1 | Batch send only; surrounding integration steps are documented workflows |
| Speed Analysis Lab | Shipped | 13 | Report/list POSTs are treated as reads; event create/delete are writes |
| Data Connect | Excluded by product choice | n/a | Warehouse sync product, not this REST CLI |
| Web Tag | Excluded by product choice | n/a | Customer-code tag API |
| WebView tracking | Excluded by product choice | n/a | Customer-code implementation API |
| Android, iOS, React Native SDKs | Excluded by product choice | n/a | Mobile SDK APIs, not server-side REST CLI commands |

## OAuth

| Method | Path | CLI command | Safety | Status |
|---|---|---|---|---|
| POST | `/v1/oauth/token` | `contentsquare-safe-cli auth check` | Secret-redacted read | Shipped |
| POST | `/v1/oauth/me` | `contentsquare-safe-cli auth me` | Secret-redacted read | Shipped |

OAuth follows the official Contentsquare request shape. Token calls send `client_id`, `client_secret`, `grant_type: client_credentials`, a documented API-family `scope`, and optional account-level `project_id`. The default scopes are `data-export` for Data Export, `metrics` for Metrics, `enrichment` for Enrichment, and `speed-analysis` for Speed Analysis Lab. `auth check` defaults to `data-export` and supports `--scope` for an explicit official override. Because Contentsquare documents Enrichment as a single non-combinable scope, combined overrides that include `enrichment` are refused. `auth me` sends the documented `client_id` / `client_secret` body to `/v1/oauth/me`.

## Data Export

| Method | Path | CLI command | Safety | Status |
|---|---|---|---|---|
| POST | `/v1/exports` | `data-export create-job` | Dry-run plan, reviewed apply | Shipped |
| GET | `/v1/exports` | `data-export list-jobs` | Read | Shipped |
| GET | `/v1/exports/successful-runs` | `data-export list-successful-runs` | Read | Shipped |
| GET | `/v1/exports/{jobId}` | `data-export get-job --job-id` | Read | Shipped |
| GET | `/v1/exports/{jobId}/runs` | `data-export list-runs --job-id` | Read | Shipped |
| GET | `/v1/exports/{jobId}/runs/{runId}` | `data-export get-run --job-id --run-id-value` | Read | Shipped |
| GET | `/v1/exportable-fields` | `data-export exportable-fields` | Read | Shipped |
| GET | `/v1/custom-vars` | `data-export custom-vars` | Read | Shipped |
| GET | `/v1/dynamic-var-keys` | `data-export dynamic-var-keys` | Read | Shipped |

Data Export read filters use the official documented query names in the API request: `state`, `order`, `format`, `frequency`, `scope`, `page`, `limit`, `from`, and `to`, depending on the endpoint. The CLI flag `--scope-filter` is the Data Export query filter and is separate from the OAuth `--scope` override.

`data-export download-run-file` is a helper, not a separate Contentsquare endpoint. It first reads the documented run endpoint and only downloads a URL returned by `payload.files[].url`. If the run has more than one file, the user must choose with `--file-index` or `--part-id`.

## Metrics objects

| Method | Path | CLI command | Status |
|---|---|---|---|
| GET | `/v1/segments` | `metrics segments` | Shipped |
| GET | `/v1/goals` | `metrics goals` | Shipped |
| GET | `/v1/mappings` | `metrics mappings` | Shipped |
| GET | `/v1/mappings/{mappingId}` | `metrics mapping --mapping-id` | Shipped |
| GET | `/v1/mappings/{mappingId}/page-groups` | `metrics page-groups --mapping-id` | Shipped |
| GET | `/v1/page-groups/{pageGroupId}` | `metrics page-group --page-group-id` | Shipped |
| GET | `/v1/page-groups/{pageGroupId}/zonings` | `metrics zonings --page-group-id` | Shipped |
| GET | `/v1/zonings/{zoningId}/zones` | `metrics zones --zoning-id` | Shipped |

## Metrics site rows

Commands are `metrics site <name>`.

`all`, `bounce-rate`, `cart-average`, `conversions`, `conversion-rate`, `pageview-average`, `revenue`, `session-time-average`, `visits`.

## Metrics page group rows

Commands are `metrics page-group-metric <name> --page-group-id`.

`all`, `activity-rate`, `bounce-rate`, `conversion-rate`, `exit-rate`, `fold-height`, `interaction-time`, `landing-rate`, `loading-time`, `page-height`, `scroll-rate`, `elapsed-time`, `unique-visits`, `views`, `views-visits`, `visits`, `web-vitals`.

## Metrics zone web rows

Commands are `metrics zone-web <name> --zone-id`.

`all`, `attractiveness-rate`, `click-rate`, `click-recurrence`, `conversion-rate-per-click`, `conversion-rate-per-hover`, `engagement-rate`, `exposure-rate`, `exposure-time`, `hesitation`, `hover-rate`, `hover-time`, `number-of-clicks`, `revenue`, `revenue-per-click`, `time-before-first-click`.

## Metrics zone app rows

Commands are `metrics zone-app <name> --zone-id`.

`all`, `conversion-rate-per-tap`, `revenue`, `revenue-per-tap`, `swipe-rate`, `swipe-recurrence`, `tap-rate`, `tap-recurrence`, `time-before-first-tap`.

Metrics read filters keep friendly CLI names, but the API request uses official Contentsquare names such as `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `period`, and `ids` where the endpoint supports them.

## Enrichment

| Method | Path | CLI command | Safety | Status |
|---|---|---|---|---|
| POST | `/v1/enrichments` | `enrichment send-batch --integration-id --body-json` | Dry-run plan, reviewed apply, no-snapshot ack | Shipped |

The docs also describe creating integration schemas, installing integrations, retrieving session IDs from the customer site, updating schemas, and updating an enrichment. Those are provider, customer-code, or Contentsquare-console workflows around the public endpoint, not additional public REST endpoints in the current docs.

## Speed Analysis Lab

| Method | Path | CLI command | Safety | Status |
|---|---|---|---|---|
| POST | `/v1/speed-analysis/analysis/report` | `speed-analysis analysis-report --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/analysis/har` | `speed-analysis analysis-har --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/monitoring/list` | `speed-analysis monitoring-list --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/monitoring/last-report` | `speed-analysis monitoring-last-report --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/monitoring/reports` | `speed-analysis monitoring-reports --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/scenario/list` | `speed-analysis scenario-list --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/scenario/report` | `speed-analysis scenario-report --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/scenario/reports` | `speed-analysis scenario-reports --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/scenario/step/report` | `speed-analysis scenario-step-report --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/scenario/report/har` | `speed-analysis scenario-report-har --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/event/list` | `speed-analysis event-list --body-json` | POST read | Shipped |
| POST | `/v1/speed-analysis/event/create` | `speed-analysis event-create --body-json` | Dry-run plan, reviewed apply, no-snapshot ack | Shipped |
| POST | `/v1/speed-analysis/event/delete` | `speed-analysis event-delete --body-json` | Dry-run plan, reviewed apply, no-snapshot and irreversible ack | Shipped |

## Documented limits to preserve

- Data Export and Metrics: 10 concurrent requests per project.
- Data Export generated files expire after 7 days.
- Data Export one-time jobs have a documented 7-day extraction limit when applicable.
- Metrics date ranges cannot exceed 92 days.
- Enrichment batch size is documented as 200.
- Enrichment has documented session limits and session age caveats.
