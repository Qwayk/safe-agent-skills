# API coverage

These are the Awin requests the tool can make. [Run a command](command_reference.md) or [check the test results](proof.md).

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
| POST `/advertisers/{advertiserId}/transactions/batch` | batch validate (approve/decline/amend/amendTrackingParameters) | `transactions batch validate` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out`, `--receipt-out` | Local validation enforces action/object requirements, target selection, and max 40,000 actions before request. Sends a JSON array and reads the returned batch or transaction status. Auth uses `Authorization: Bearer <token>` plus `accessToken=<token>` for parity with other non-conversion transaction commands. The batch page is ambiguous in docs (`accessToken` appears as a header label), so the command uses the documented bearer-plus-query pattern. |
| GET `/advertisers/{advertiserId}/transactions/jobs` | transaction job status list | `transactions jobs list` | implemented | none | Header-only `Bearer`. |
| GET `/advertisers/{advertiserId}/transactions/jobs/{jobId}` | transaction job status detail | `transactions jobs show` | implemented | none | Header-only `Bearer` with optional `output` query param (`errors` or `all`). |
| POST `/s2s/advertiser/{advertiser_id}/orders` | conversion order posting | `conversion orders create` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | `x-api-key` only. `orders` required. Supports dry-run by default with optional `--webhook-url` and receipt output on apply. |
| GET `/advertisers/{advertiserId}/reports/publisher` | publisher reporting | `reports publisher` | implemented | none | Uses `Authorization: Bearer <token>` plus `accessToken=<token>` query param. Supported filters: `startDate`, `endDate`, optional `dateType`, `timezone`. |
| GET `/advertisers/{advertiserId}/reports/campaign` | campaign reporting | `reports campaign` | implemented | none | Uses `Authorization: Bearer <token>` plus `accessToken=<token>` query param. Supports `startDate`, `endDate`, `campaign`, `publisherIds`, `includeNumbersWithoutCampaign`, `interval`, and `timezone`. `--date-type` is not supported on this command. |
| GET `/advertisers/{advertiserId}/publishers` | publisher accounts for advertiser | `auth check`, `publishers list` | implemented | read-only | Both shipped commands use the same official publishers endpoint. `auth check` is the auth smoke command, and `publishers list` is the full list read. Uses `Authorization: Bearer <token>` and `accessToken=<token>` query param. |
| POST `/promotion/advertiser/{advertiser_id}` | offers create | `offers create` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | Bearer header only. One offer per request with required fields/validation. |
| POST `/advertisers/{ADVERTISER_ID}/awinfeeds/{VERTICAL}/{LOCALE}/products` | product-feeds upload | `product-feeds upload` | implemented | `--apply --yes --ack-irreversible --plan-in`, `--plan-out` | Bearer header only. JSONL body requires `id`, `title`, `description`, `link`, `image_link`. Uses `application/jsonlines` and checks returned product count, feed version and errors. |

## Implementation notes and live limits

- The table covers the legacy advertiser routes this tool ships. See [Awin's authentication guide](https://help.awin.com/apidocs/api-authentication) for its newer API and current access requirements.
- Batch validation still sends Bearer auth and `accessToken` in the query. Awin's batch page lists `accessToken` under headers, and live acceptance of the current form remains unverified.
- The CLI saves review plans and records what Awin returns. No live advertiser run is recorded in [the test results](proof.md).
