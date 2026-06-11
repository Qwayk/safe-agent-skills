# Skimlinks API Coverage

Last verified: **2026-06-08**

This is the source of truth for the Skimlinks command surface. It accounts for the official Skimlinks developer-center boundary and the shipped v0.1.0 CLI surface.

## Official Sources

- Developer center: `https://developers.skimlinks.com/`
- Merchant API page: `https://developers.skimlinks.com/merchant.html`
- Merchant API blueprint: `https://skimlinksmerchantapi.docs.apiary.io/api-description-document`
- Reporting API page: `https://developers.skimlinks.com/reporting.html`
- Reporting API blueprint: `https://skimlinksreporting.docs.apiary.io/api-description-document`
- Product Key page: `https://developers.skimlinks.com/product-key.html`
- Product Key blueprint: `https://skimlinksproducts.docs.apiary.io/api-description-document`
- Link Wrapper page: `https://developers.skimlinks.com/link.html`
- Link Wrapper Apiary JSON: `https://jsapi.apiary.io/apis/skimlinkslinkapi`
- Data Pipe page: `https://developers.skimlinks.com/data-pipe.html`
- Data Pipe blueprint: `https://datapipe1.docs.apiary.io/api-description-document`
- Skimlinks JavaScript page: `https://developers.skimlinks.com/skimlinks-script.html`
- Skimlinks JavaScript Apiary JSON: `https://jsapi.apiary.io/apis/skimjs`

## Coverage Rules

- The shipped CLI uses explicit named commands only.
- There is no raw request, generic bridge, arbitrary URL caller, or call-anything command.
- Merchant API, Reporting API, and Product Key use the temporary token endpoint at `https://authentication.skimapis.com/access_token`.
- Product Key may require separate enabled credentials, so the CLI must support product-specific credentials instead of pretending all access tiers are identical.
- Link Wrapper is an official URL-construction surface, not a JSON API. It is covered by a deterministic local URL builder.
- Data Pipe is an official managed data-delivery guide. It is not a normal Skimlinks request/response API surface.
- Skimlinks JavaScript is official browser-side implementation guidance. It is not a normal Skimlinks request/response API surface.

## Locked Command Families

| Family | Command | Treatment | Notes |
| --- | --- | --- | --- |
| Auth | `auth check` | Shipped command | Exchanges credentials for a temporary access token and reports access status without printing secrets. |
| Onboarding | `onboarding` | Shipped command | Prints setup steps and can create `.env` placeholders only. |
| Runs | `runs list`, `runs show` | Shipped command | Exposes local run history once implementation creates `.state/runs/`. |
| Merchant API | `merchant merchants list` | Shipped command | Current v4 Merchant API. |
| Merchant API | `merchant domains list` | Shipped command | Current v4 Merchant API. |
| Merchant API | `merchant verticals list` | Shipped command | Current v4 Merchant API. |
| Merchant API | `merchant alternative-verticals list` | Shipped command | Current v4 Merchant API. |
| Merchant API | `merchant offers list` | Shipped command | Current v4 Merchant API. |
| Reporting API | `reporting commissions search` | Shipped command | Individual commission report. |
| Reporting API | `reporting aggregated get` | Shipped command | Hub-style aggregated performance report. |
| Reporting API | `reporting link-report query` | Shipped command | Multi-aggregated link report, NDJSON response. |
| Reporting API | `reporting link-report dimensions` | Shipped command | Official helper endpoint named in the link report docs. |
| Reporting API | `reporting link-report metrics` | Shipped command | Official helper endpoint named in the link report docs. |
| Reporting API | `reporting page-report query` | Shipped command | Multi-aggregated page report, NDJSON response. |
| Reporting API | `reporting page-report dimensions` | Shipped command | Official helper endpoint named in the page report docs. |
| Reporting API | `reporting page-report metrics` | Shipped command | Official helper endpoint named in the page report docs. |
| Reporting API | `reporting trending-products get` | Shipped command | Trending products report. |
| Reporting API | `reporting product-report get` | Shipped command | Product bought report. |
| Reporting API | `reporting payment-status get` | Shipped command | Payment status report. |
| Reporting API | `reporting deactivated-merchants get` | Shipped command | Deactivated merchants report. |
| Product Key | `product-key product get` | Shipped command | Single product details and alternatives lookup. |
| Product Key | `product-key products get` | Shipped command | Read-like POST for multiple product details and alternatives. |
| Link Wrapper | `link-wrapper build` | Shipped command | Builds an official `https://go.skimresources.com/` URL. No live write. |
| Data Pipe | None | Accounted for, not shipped as API command | Official guide describes Skimlinks-managed daily export files delivered to S3/GCS, not an HTTP API command surface. |
| Skimlinks JavaScript | None | Accounted for, not shipped as API command | Official browser-side settings and HTML/JS guidance, not an HTTP API command surface. |

## Authentication And Configuration

| Scope | Required config | Notes |
| --- | --- | --- |
| Merchant API | `SKIMLINKS_CLIENT_ID`, `SKIMLINKS_CLIENT_SECRET`, `SKIMLINKS_PUBLISHER_ID` | Uses `https://authentication.skimapis.com/access_token`, then sends `access_token` as a query parameter per official docs. |
| Reporting API | `SKIMLINKS_CLIENT_ID`, `SKIMLINKS_CLIENT_SECRET`, `SKIMLINKS_PUBLISHER_ID` | Uses the same temporary-token flow as Merchant API. |
| Product Key | `SKIMLINKS_PRODUCT_CLIENT_ID`, `SKIMLINKS_PRODUCT_CLIENT_SECRET`, `SKIMLINKS_PUBLISHER_ID`, `SKIMLINKS_PUBLISHER_DOMAIN_ID` or `--publisher-domain-id` | Product-specific credentials are preferred. If product-specific values are absent, implementation may fall back to shared credentials but must report that Product Key access can still be disabled by Skimlinks. Official Product Key docs require `publisher_domain_id` for both Product Key operations. |
| Link Wrapper | `SKIMLINKS_LINK_WRAPPER_ID` | The official docs call this the domain-specific ID and show it as the `id` query parameter. |
| Publisher domain filters | `SKIMLINKS_PUBLISHER_DOMAIN_ID` or `--publisher-domain-id` | Optional default for Merchant commands that support a publisher domain ID filter; required for Product Key commands. |

## Merchant API

Base URL: `https://merchants.skimapis.com/`

| Official operation | Method | Path | Command | Status | Coverage note |
| --- | --- | --- | --- | --- | --- |
| List / Search Merchants | GET | `/v4/publisher/{publisher_id}/merchants` | `merchant merchants list` | Shipped in v0.1.0 | Supports official filters including publisher domain, search, vertical, merchant IDs, country, favourite type, pagination, sorting, advertiser ID, and alternative vertical filters. |
| List Domains | GET | `/v4/publisher/{publisher_id}/domains` | `merchant domains list` | Shipped in v0.1.0 | Requires publisher ID and access token. |
| List Verticals | GET | `/v4/verticals` | `merchant verticals list` | Shipped in v0.1.0 | Public v4 vertical list in the current blueprint. |
| List Alternative Verticals | GET | `/v4/alternative_verticals` | `merchant alternative-verticals list` | Shipped in v0.1.0 | Public v4 alternative vertical list in the current blueprint. |
| List / Search Offers | GET | `/v4/publisher/{publisher_id}/offers` | `merchant offers list` | Shipped in v0.1.0 | Supports official filters including search, merchant ID, vertical, country, period, favourite type, pagination, sorting, and advertiser ID. |

### Merchant Legacy V3

The official Merchant blueprint still includes an `OLD version` group for v3. The CLI does not ship v3 commands in the initial customer-ready surface because v4 is the current documented API and covers the same merchant/domain/vertical/offer capabilities with the current temporary-token auth flow.

| Official legacy operation | Method | Path | Command | Status | Coverage note |
| --- | --- | --- | --- | --- | --- |
| OLD List / Search Merchants | GET | `/v3/merchants` | None | Accounted for, legacy duplicate not shipped | Uses old `apikey`, `account_type`, and `account_id` query auth. |
| OLD List Domains | GET | `/v3/domains` | None | Accounted for, legacy duplicate not shipped | Superseded by v4 domains command. |
| OLD List Verticals | GET | `/v3/verticals` | None | Accounted for, legacy duplicate not shipped | Superseded by v4 verticals command. |
| OLD List / Search Offers | GET | `/v3/offers` | None | Accounted for, legacy duplicate not shipped | Superseded by v4 offers command. |

## Reporting API

Base URL: `https://reporting.skimapis.com/`

| Official operation | Method | Path | Command | Status | Coverage note |
| --- | --- | --- | --- | --- | --- |
| Search Commissions | GET | `/publisher/{publisher_id}/commission-report` | `reporting commissions search` | Shipped in v0.1.0 | Supports official filters including date range, updated since, custom ID, merchant ID, advertiser ID, domain ID, commission ID, status, commission type, pagination, and sorting. |
| Get Performance Data Grouped By Date, Merchant, Page, Link, Domain, Country, Device or Network Payout Type | GET | `/publisher/{publisher_id}/reports` | `reporting aggregated get` | Shipped in v0.1.0 | Hub-style aggregated report. Supports required `report_by`, `start_date`, and `end_date`. |
| Get Performance Link Data Grouped by Multiple Fields | GET | `/publisher/{publisher_id}/aggregation/v1/link-report` | `reporting link-report query` | Shipped in v0.1.0 | Returns NDJSON. Supports repeated `dim` and `met` query params. |
| Link report dimensions | GET | `/publisher/{publisher_id}/aggregation/v1/link-report/dimensions` | `reporting link-report dimensions` | Shipped in v0.1.0 | Helper endpoint named in the official link-report docs. |
| Link report metrics | GET | `/publisher/{publisher_id}/aggregation/v1/link-report/metrics` | `reporting link-report metrics` | Shipped in v0.1.0 | Helper endpoint named in the official link-report docs. |
| Get Performance Page Data Grouped by Multiple Fields | GET | `/publisher/{publisher_id}/aggregation/v1/page-report` | `reporting page-report query` | Shipped in v0.1.0 | Returns NDJSON. Supports repeated `dim` and `met` query params. |
| Page report dimensions | GET | `/publisher/{publisher_id}/aggregation/v1/page-report/dimensions` | `reporting page-report dimensions` | Shipped in v0.1.0 | Helper endpoint named in the official page-report docs. |
| Page report metrics | GET | `/publisher/{publisher_id}/aggregation/v1/page-report/metrics` | `reporting page-report metrics` | Shipped in v0.1.0 | Helper endpoint named in the official page-report docs. |
| Get trending products | GET | `/publisher/{publisher_id}/trending-products` | `reporting trending-products get` | Shipped in v0.1.0 | Supports official period, sort, advertiser, country, vertical, search, pagination, and audience-country filters. |
| Get product bought | GET | `/publisher/{publisher_id}/product-report` | `reporting product-report get` | Shipped in v0.1.0 | Product bought report. Docs note it only covers some networks. |
| Get payment status | GET | `/publisher/{publisher_id}/payment-status` | `reporting payment-status get` | Shipped in v0.1.0 | Payment status report with invoice filters. |
| Get deactivated merchants | GET | `/publisher/{publisher_id}/deactivated-merchants` | `reporting deactivated-merchants get` | Shipped in v0.1.0 | Requires official sort and minimum commission parameters. |

## Product Key

Base URL: `https://products.skimapis.com/`

| Official operation | Method | Path | Command | Status | Coverage note |
| --- | --- | --- | --- | --- | --- |
| Get Product Details and Alternatives | GET | `/v2/publisher/{publisher_id}/product` | `product-key product get` | Shipped in v0.1.0 | Required query params include `access_token` and `publisher_domain_id`, plus one product selector such as `product_url`, `product_keywords`, `upc`, or `product_id`. `sort_desc` is the official string value `asc` or `desc`, default `desc`. The docs also list `/publisher/{publisher_id}/product` and `/v2/publisher/{publisher_id}/get-products` aliases for this operation. The CLI uses the v2 product path by default and records aliases in output metadata. |
| Get Multi Product Details and Alternatives | POST | `/v1/publisher/{publisher_id}/products` | `product-key products get` | Shipped in v0.1.0 | Required query params include `access_token` and `publisher_domain_id`. Request body requires `product_urls` or `product_ids`. `sort_desc` is the official string value `asc` or `desc`, default `desc`. This is a read-like POST and does not mutate Skimlinks data or use `--apply`. |

## Link Wrapper

Base URL: `https://go.skimresources.com/`

| Official operation | Method | Path | Command | Status | Coverage note |
| --- | --- | --- | --- | --- | --- |
| Build monetized redirect URL | URL construction | `/?id={domain_specific_id}&url={encoded_url}` | `link-wrapper build` | Shipped in v0.1.0 | Official parameters are required `id` and `url`, plus optional `xcust` and `sref`. The CLI builds the URL locally and can optionally validate encoding. It does not click or follow the redirect by default. |

## Data Pipe

Data Pipe is accounted for in the official boundary but is not a shipped API command family.

| Official area | Command | Status | Coverage note |
| --- | --- | --- | --- |
| Data Pipe setup guide | None | Accounted for, not a CLI API surface | The official docs describe a Skimlinks-managed export pipeline that delivers daily data to Google Cloud Storage or Amazon S3. |
| Data layout | None | Accounted for, not a CLI API surface | The docs define exported partitions and files for clicks, pages, commissions, and products purchased. |
| Example data queries | None | Accounted for, not a CLI API surface | The docs provide downstream SQL examples, not Skimlinks API endpoints. |

## Skimlinks JavaScript

Skimlinks JavaScript is accounted for in the official boundary but is not a shipped API command family.

| Official area | Command | Status | Coverage note |
| --- | --- | --- | --- |
| Basic browser usage | None | Accounted for, browser-side docs only | Covers `noskim` and `noskimlinks` classes for excluding content or links. |
| Domain-level settings | None | Accounted for, browser-side docs only | These settings are changed in Skimlinks Hub, not through a documented API in this source. |
| Page-level settings | None | Accounted for, browser-side docs only | Covers the `skimlinks_settings` JavaScript object and settings such as `noskim`, `noskimlinks`, `noskimwords`, include/exclude lists, target, tracking, and custom rel. |
| Skimlinks Custom ID | None | Accounted for, browser-side docs only | Documents page-level and link-level tracking values that later appear in reports. |

## Build Status

Rows marked `Shipped in v0.1.0` are implemented in code and must stay aligned with tests, docs, examples, and proof.
