# API coverage - Sovrn

Purpose:
- Lock the exact official Sovrn HTTP surface before scaffolding or broad code work.
- Keep coverage honest across Commerce HTTP APIs, Advertising Reporting APIs, and docs-only support pages.
- Preserve the real auth split instead of flattening it into one fake auth model.

## Summary

- Provider: Sovrn Developer Center
- Product shape: one combined safe CLI for official Sovrn Commerce HTTP APIs plus official Sovrn Advertising Reporting APIs
- Last audited (UTC): 2026-06-08
- Coverage state: endpoint map locked; all mapped CLI command families are implemented; proof/examples are still being filled in
- Surface count: 22 official HTTP endpoint rows plus 1 official non-HTTP affiliate-link pattern accounted for separately

## Auth split to preserve

- Commerce secret header: `Authorization: secret {SECRET_KEY}`
- Commerce site API key: query or path key such as `key`, `apiKey`, `api_key`, or `{site-api-key}`
- Advertising reporting: `x-api-key` header plus `publisherId` path value

## Shipped HTTP surface

Status meanings:
- `implemented` = official endpoint confirmed and a matching named CLI command is implemented
- `implemented-access-gated` = named CLI command is implemented, but vendor access or registration is still required before live success is possible

| Product area | Endpoint | Capability | Official doc | Auth shape | Planned CLI command | State | Notes |
|---|---|---|---|---|---|---|---|
| Commerce account | `GET https://rest.viglink.com/api/account/campaigns/{search}` | List campaigns or search by name or campaign ID | `reference/campaigns.md` | Commerce secret header | `sovrn-safe-cli commerce campaigns get` | `implemented` | `search` defaults to `PRIMARY` in the official doc |
| Commerce links | `GET https://api.viglink.com/api/link/` | Check whether a URL can be monetized | `reference/link.md` | Commerce site API key in query `key` | `sovrn-safe-cli commerce links check` | `implemented` | Link-check flow, not write |
| Commerce links | `GET https://api.viglink.com/api/bid` | Request a real-time bid for a click | `reference/getbid.md` | Commerce site API key in query `key` | `sovrn-safe-cli commerce links bid-check` | `implemented` | Uses real user IP and user agent; click-routing helper only |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/transactions` | Query transaction-level commission events | `reference/get_reports-transactions.md` | Commerce secret header | `sovrn-safe-cli commerce reports transactions get` | `implemented` | Official OpenAPI names the scheme `bearerAuth`, but the doc and examples use `Authorization: secret ...` |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/pages` | Query page-level performance | `reference/get_reports-pages.md` | Commerce secret header | `sovrn-safe-cli commerce reports pages get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/links` | Query link-level performance | `reference/get_reports-links.md` | Commerce secret header | `sovrn-safe-cli commerce reports links get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/merchants` | Query merchant-level performance | `reference/get_reports-merchants.md` | Commerce secret header | `sovrn-safe-cli commerce reports merchants get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/merchantsbydate` | Query merchant performance by day | `reference/get_reports-merchantsbydate.md` | Commerce secret header | `sovrn-safe-cli commerce reports merchants-by-date get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/merchandise` | Query product-level merchandise performance | `reference/get_reports-merchandise.md` | Commerce secret header | `sovrn-safe-cli commerce reports merchandise get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/networks` | Query network-level performance | `reference/get_reports-networks.md` | Commerce secret header | `sovrn-safe-cli commerce reports networks get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce real-time reports | `GET https://viglink.io/v1/reports/cuids` | Query CUID-level performance | `reference/get_reports-cuids.md` | Commerce secret header | `sovrn-safe-cli commerce reports cuids get` | `implemented` | `clickDateStart` and `clickDateEnd` required |
| Commerce merchants | `POST https://viglink.io/merchants/rates/summaries` | Retrieve approved merchants with optional filters | `reference/post_summaries.md` | Commerce secret header | `sovrn-safe-cli commerce merchant-groups approved` | `implemented` | Query `campaignId` plus JSON body filters |
| Commerce merchants | `GET https://viglink.io/merchants/rates/summaries/delta` | Retrieve only updated merchants since a timestamp or ETag | `reference/get_summaries-delta.md` | Commerce secret header | `sovrn-safe-cli commerce merchant-groups delta` | `implemented` | Requires `campaignId` and either `since` or `If-None-Match` |
| Commerce coupons | `GET https://viglink.io/coupons/product` | Retrieve product-specific promo codes | `reference/get_product.md` | Commerce secret header plus site API key query `api_key` | `sovrn-safe-cli commerce coupons product get` | `implemented-access-gated` | Official page says registration is required |
| Commerce product APIs | `POST https://shopping-gallery.prd-commerce.sovrnservices.com/ai-orchestration/products` | Generate product recommendations from content | `reference/get_product_recommendations.md` | Commerce site API key in query `apiKey` | `sovrn-safe-cli commerce products recommend` | `implemented` | Server-side HTTP API; separate from browser-side shopping gallery docs |
| Commerce product APIs | `GET https://comparisons.sovrn.com/api/affiliate/v3.5/sites/{site-api-key}/compare/prices/{market}/by/accuracy` | Find alternative merchants and prices for a product | `reference/product-affiliate-api.md` | Commerce secret header plus site API key in path | `sovrn-safe-cli commerce comparisons prices search` | `implemented` | Requires one of `barcode`, `plainlink`, or `search-keywords` |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/account` | Get account-level reporting data | `reference/get_reporting-advertising-publishers-publisherid-account-2.md` | Advertising `x-api-key` header plus `publisherId` path | `sovrn-safe-cli advertising reports account get` | `implemented` | Hidden endpoint page linked from official Advertising support docs |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/bid` | Get account-level bid reporting data | `reference/get_reporting-advertising-publishers-publisherid-bid-2.md` | Advertising `x-api-key` header plus `publisherId` path | `sovrn-safe-cli advertising reports bid get` | `implemented` | Hidden endpoint page linked from official Advertising support docs |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/breakout` | Get account-level site breakout data | `reference/get_reporting-advertising-publishers-publisherid-breakout-2.md` | Advertising `x-api-key` header plus `publisherId` path | `sovrn-safe-cli advertising reports breakout get` | `implemented` | Hidden endpoint page linked from official Advertising support docs |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/domains/{domainName}/account` | Get domain-level reporting data | `reference/get_reporting-advertising-publishers-publisherid-domains-domainname-account-2.md` | Advertising `x-api-key` header plus `publisherId` and `domainName` path values | `sovrn-safe-cli advertising reports domain-account get` | `implemented` | Hidden endpoint page linked from official Advertising support docs |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/domains/{domainName}/bid` | Get domain-level bid reporting data | `reference/get_reporting-advertising-publishers-publisherid-domains-domainname-bid-2.md` | Advertising `x-api-key` header plus `publisherId` and `domainName` path values | `sovrn-safe-cli advertising reports domain-bid get` | `implemented` | Hidden endpoint page linked from official Advertising support docs |
| Advertising reporting | `GET https://api.sovrn.com/reporting/advertising/publishers/{publisherId}/` | Get custom reporting data for a publisher | `reference/get_reporting-advertising-publishers-publisherid-1.md` | Advertising `x-api-key` header plus `publisherId` path | `sovrn-safe-cli advertising reports custom get` | `implemented` | Requires `start`, `end`, `metrics`, `dimensions`, and `granularity` |

## Command family lock

Top-level command families are locked as:

- `commerce campaigns`
- `commerce links`
- `commerce reports`
- `commerce merchant-groups`
- `commerce coupons`
- `commerce products`
- `commerce comparisons`
- `advertising reports`

No generic raw-request bridge is allowed to fill coverage gaps.

## Official support material accounted for but not shipped as HTTP CLI surface

| Official page | How it is treated | Why |
|---|---|---|
| `reference/building-affiliate-links.md` | `official-non-http-pattern` | Official affiliate-link construction pattern; excluded from shipped HTTP endpoint coverage, but should stay visible in the ledger |
| `docs/authorization.md` | `support-material` | Commerce auth guide used for secret-header rules |
| `docs/overview-1.md` | `out-of-scope-browser-docs` | Commerce JavaScript overview, not server-side CLI HTTP surface |
| `docs/configuration-with-html.md` | `out-of-scope-browser-docs` | Commerce JavaScript HTML config, not server-side CLI HTTP surface |
| `docs/configuration-with-javascript.md` | `out-of-scope-browser-docs` | Commerce JavaScript config, not server-side CLI HTTP surface |
| `docs/javascript-api.md` | `out-of-scope-browser-docs` | Browser JavaScript API, not shipped CLI surface |
| `docs/comparisons-automated-library.md` | `support-material` | Comparison library guide, not a documented HTTP endpoint |
| `docs/server-side-rendering.md` | `support-material` | Shopping gallery integration guide, not a standalone CLI endpoint |
| `docs/mcp.md` | `out-of-scope-mcp-beta` | MCP beta docs are not shipped CLI coverage |
| `docs/mcp-demos.md` | `out-of-scope-mcp-beta` | Demo prompts only |
| `reference/getting-started-1.md` | `support-material` | Advertising setup page used to discover hidden endpoint docs |
| `reference/authorization-1.md` | `support-material` | Advertising auth page used to confirm `x-api-key` rules |
| `reference/account-level-1.md` | `support-material` | Advertising support page used to discover account-level hidden endpoint docs |
| `reference/domain-level-1.md` | `support-material` | Advertising support page used to discover domain-level hidden endpoint docs |
| `reference/custom-reporting.md` | `support-material` | Overview page for Advertising custom reporting; actual endpoint row uses the linked hidden endpoint doc |

## Known documentation notes

- The official Advertising category exposes some endpoint docs only through support pages, not as visible endpoint rows in the main reference index. This ledger includes those hidden official endpoint pages so coverage stays honest.
- The Commerce real-time report OpenAPI docs use the security-scheme name `bearerAuth`, but the same official pages and examples still require `Authorization: secret {SECRET_KEY}`. This tool should treat them as secret-header auth, not OAuth bearer tokens.
- Commerce link and bid commands must stay separate from secret-header flows because they use the site API key path instead.
- The official affiliate-link construction page is accounted for separately as a non-HTTP pattern so the tool does not over-claim HTTP coverage.
- Commerce coupon and price-comparison commands must keep split auth visible because they need both a secret header and a site key.
- Browser JavaScript docs, shopping-gallery browser docs, and MCP beta docs must stay listed as support or out-of-scope rows unless the product choice changes later.
