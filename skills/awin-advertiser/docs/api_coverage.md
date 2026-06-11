# API coverage

## Summary

- Provider: Awin Advertiser API
- API base URL: `https://api.awin.com`
- Auth method: mixed (documented below)
- Last audited (UTC): 2026-06-09

## Endpoint coverage

| Endpoint | Capability | CLI command(s) | Status | Safety gates | Notes |
|---|---|---|---|---|---|
| GET `/advertisers/{advertiserId}/transactions/` | list transactions | `transactions list` | implemented | none | Officially used list endpoint; query uses `startDate`, `endDate`, optional `dateType`, `publisherId`, `status`, `timezone`, and `showBasketProducts`. |
| GET `/advertisers/{advertiserId}/transactions` | transactions by ids | `transactions by-ids` | implemented | none | Implemented now for comma-separated `ids` lookups; shares request shape with list endpoint except path and ID query. |
| POST `/advertisers/{advertiserId}/transactions/batch` | batch validate (approve/decline/amend/amendTrackingParameters) | `transactions batch validate` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out`, `--receipt-out` | Local validation enforces action/object requirements, target selection, and max 40,000 actions before request. Apply path posts JSON array to endpoint and rejects provider responses with failure markers. Auth uses `Authorization: Bearer <token>` plus `accessToken=<token>` for deterministic parity with other non-conversion transaction commands. Batch page is ambiguous in docs (`accessToken` appears as a header label); this tool uses a documented deterministic choice. |
| GET `/advertisers/{advertiserId}/transactions/jobs` | transaction job status list | `transactions jobs list` | implemented | none | Header-only `Bearer`. |
| GET `/advertisers/{advertiserId}/transactions/jobs/{jobId}` | transaction job status detail | `transactions jobs show` | implemented | none | Header-only `Bearer` with optional `output` query param (`errors` or `all`). |
| POST `/s2s/advertiser/{advertiser_id}/orders` | conversion order posting | `conversion orders create` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | `x-api-key` only. `orders` required. Supports dry-run by default with optional `--webhook-url` and receipt output on apply. |
| GET `/advertisers/{advertiserId}/reports/publisher` | publisher reporting | `reports publisher` | implemented | none | Uses `Authorization: Bearer <token>` plus `accessToken=<token>` query param. Supported filters: `startDate`, `endDate`, optional `dateType`, `timezone`. |
| GET `/advertisers/{advertiserId}/reports/campaign` | campaign reporting | `reports campaign` | implemented | none | Uses `Authorization: Bearer <token>` plus `accessToken=<token>` query param. Supports `startDate`, `endDate`, `campaign`, `publisherIds`, `includeNumbersWithoutCampaign`, `interval`, and `timezone`. `--date-type` is not supported on this command. |
| GET `/advertisers/{advertiserId}/publishers` | publisher accounts for advertiser | `auth check`, `publishers list` | implemented | read-only | Both shipped commands use the same official publishers endpoint. `auth check` is the auth smoke command, and `publishers list` is the full list read. Uses `Authorization: Bearer <token>` and `accessToken=<token>` query param. |
| POST `/promotion/advertiser/{advertiser_id}` | offers create | `offers create` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | Bearer header only. One offer per request with required fields/validation. |
| POST `/advertisers/{ADVERTISER_ID}/awinfeeds/{VERTICAL}/{LOCALE}/products` | product-feeds upload | `product-feeds upload` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | Bearer header only. JSONL body requires `id`, `title`, `description`, `link`, `image_link`. Response success checks body for validation errors even on HTTP 200. |

## Implementation notes and live limits

- `publishers`, `transactions`, `transactions/jobs`, reports, offers, product-feeds, conversion orders create, and transaction batch validate are implemented as deterministic JSON in this tool.
- `transactions/jobs`, `offers`, and `product-feeds` use header-only bearer auth; `publishers`, `transactions`, `reports`, and `transactions batch validate` use bearer + access-token query.
- Conversion uses `x-api-key` auth for POST `/s2s/advertiser/{advertiser_id}/orders`. Conversion command is dry-run by default with explicit write gates and optional plan/receipt artifacts.
- Run history is implemented for local tracking.
