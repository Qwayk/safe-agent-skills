# Changelog

All notable changes to this project are documented in this file.

This format is based on Keep a Changelog, and this project follows Semantic Versioning.
Because this tool is pre-1.0 (`0.x`), minor version bumps may include breaking changes.

## [Unreleased]

### Added
- Real Fortnox auth foundation:
  - `auth login`
  - `auth exchange-code`
  - `auth refresh`
  - `auth service-account-token`
  - live `/3/me` auth check
- Local auth/runtime tests for login URL generation, code exchange, refresh-token rotation, service-account token fetch, and auth checks.
- First accounting read commands:
  - `company-information get`
  - `company-settings get`
  - `article-url-connections list|get|create|update|delete`
  - `customers list|get`
  - `suppliers list|get`
  - `articles list|get|list-time-article-registrations`
  - `price-lists list|get`
  - `prices list|get|get-by-from-quantity|list-sublist`
  - `projects list|get`
  - `currencies list|get`
  - `cost-centers list|get`
  - `terms-of-deliveries list|get`
  - `terms-of-payments list|get`
  - `eu-vat-limit-regulation get`
  - `account-charts list`
  - `accounts list|get`
  - `financial-years list|get|create`
  - `fortnox-finans get|send-an-invoice-with-fortnox-finans|action-pause|action-report-payment|action-stop|action-take-fees|action-unpause`
  - `integration-ratings list`
  - `integration-sales get-by-app-id|get-by-app-id-and-tenant|resolves-sales-information-of-an-integration`
  - `predefined-accounts list|get|update`
  - `predefined-voucher-series list|get|update`
  - `modes-of-payments list|get`
  - `voucher-series list|get`
  - `vouchers list|get|list-by-series|list-current-financial-year|create`
  - `invoice-payments list|get|create|update|remove|bookkeep`
  - `invoice-accruals list|get|create|update|remove`
  - `asset-file-connections list|create|remove`
  - `asset-types list|get|create|update|delete`
  - `assets list|get|create|update|delete|assets-depreciation-list|change-manual-ob-value-of-an-asset|perform-a-depreciation-of-an-asset|scrap-an-asset|sell-an-asset|write-down-an-asset|write-up-an-asset`
  - `contract-accruals list|get|create|update|remove`
  - `contract-templates list|get|create|update`
  - `contracts list|get|create|update|create-invoice|increase-invoice-count|finish`
  - `supplier-invoice-accruals list|get|create|update|remove`
  - `supplier-invoice-payments list|get|create|update|remove|bookkeep`
  - `supplier-invoices list|get|create|update|approvalbookkeep|approvalpayment|bookkeep|cancel|credit`
  - `invoices list|get|preview|print|print-reminder|send-an-invoice-as-e-invoice|send-an-invoice-as-e-print|send-an-invoice-as-email`
  - `offers list|get|preview|print|send-given-offer-as-email`
  - `orders list|get|preview|print|send-given-order-as-email`
  - `offers create|update|cancel|create-invoice|create-order|externalprint`
  - `orders create|update|cancel|create-invoice|externalprint`
  - `purchase-orders list|get|get-csv|get-note|list-matches|create|update|partial-update-purchase-order|manually-complete-dropship-order|manually-complete-purchase-order|send-purchase-order-via-email|sends-multiple-purchase-orders-via-email|update-response|update-response-bulk|void`
  - `incoming-goods list|get|create|update|partial-update-incoming-goods-document|complete-incoming-goods-document|release|void`
  - `stock-points list|get|get-stock-locations|list-multi|create|update|append-stock-locations|delete`
  - `stock-taking list|get|get-candidate-rows|get-rows|create|update|add-rows|add-rows-by-filter|delete|delete-row|delete-rows|release|void`
  - `invoices create|update|bookkeep|cancel|credit|warehouseready|externalprint`
  - `accounts create|update|delete`
  - `customers create|update|delete`
  - `customer-references list|get|create|update|delete`
  - `expenses list|get|create`
  - `labels list|create|update|delete`
  - `locked-period get`
  - `print-templates list`
  - `suppliers create|update`
  - `tax-reductions list|get|create|update|remove`
  - `employees list|get|create|update`
  - `articles create|update|delete`
  - `price-lists create|update`
  - `prices create|update|update-by-from-quantity|delete`
  - `terms-of-deliveries create|update`
  - `units list|get|create|update|remove`
  - `way-of-deliveries list|get|create|update|remove`
  - `terms-of-payments create|update|remove`
  - `cost-centers create|update|remove`
  - `currencies create|update|remove`
  - `projects create|update|remove`
  - `modes-of-payments create|update|remove`
- Explicit rendered Fortnox list filters for:
  - `articles list`
  - `customers list`
  - `suppliers list`
  - the current rendered `price-lists` read docs do not show extra query params
- Completed the bookkeeping block:
  - `financial-years create`
  - `predefined-accounts update`
  - `predefined-voucher-series update`
  - `vouchers create`
- `voucher-series create|update`
- Completed the payroll/time-reporting block in the same safe apply-first style:
  - `absence-transactions list|get|get-by-employee-date-code|create|update|delete`
  - `attendance-transactions list|get|get-by-employee-date-code|create|update|delete`
  - `salary-transactions list|get|create|update|delete`
  - `schedule-times get|update|reset-day`
  - `sie get`
  - `stock-status get-stock-balance`
  - `tenant get`
  - `users fetch-user-information-for-a-single-published-integration-and-tenant`
  - `registrations get`
  - `vacation-debt-basis get`
- Completed the offers/orders/invoices write slice in the same safe apply-first style:
  - offers: `create|update|cancel|create-invoice|create-order|externalprint`
  - orders: `create|update|cancel|create-invoice|externalprint`
  - invoices: `create|update|bookkeep|cancel|credit|warehouseready|externalprint`
- Completed the contract document block in the same safe apply-first style:
  - `contract-accruals list|get|create|update|remove`
  - `contract-templates list|get|create|update`
  - `contracts list|get|create|update|create-invoice|increase-invoice-count|finish`
- Completed the document-intake read block for the currently safest official GET surfaces:
  - `archive get-root|get-file`
  - `inbox get-root|get-file`
  - `custom-document-types list|get`
  - `custom-inbound-documents get`
  - `custom-outbound-documents get`
  - `manual-documents list`
  - `manual-inbound-documents get`
  - `manual-outbound-documents get`
  - `email-senders list`
- Completed the document-intake write follow-up block in the same safe apply-first style:
  - `archive delete|remove|upload-a-file-to-a-specific-subdirectory`
  - `inbox remove|upload-a-file`
  - `custom-document-types create`
  - `custom-inbound-documents save|release|void`
  - `custom-outbound-documents save|release|void`
  - `manual-inbound-documents create|update|update-note|release|void`
  - `manual-outbound-documents create|update|update-note|release|void`
  - `email-senders add-a-new-email-address-as-trusted|delete`
- Completed the accounting helper block in the same safe apply-first style:
  - `customer-references list|get|create|update|delete`
  - `expenses list|get|create`
  - `tax-reductions list|get|create|update|remove`
  - `labels list|create|update|delete`
  - `locked-period get`
  - `print-templates list`

### Changed
- Replaced template Fortnox auth/config/onboarding docs with the real OAuth + refresh + service-account contract.
- Expanded `.env.example`, token helpers, and auth runtime plumbing to support the official Fortnox token endpoints.
- Rewrote the source README and front-door docs to match the public Fortnox skill-page contract, removed source-only wrapper links from public-facing pages, tightened the docs contract tests, and corrected stale shipped-status wording in the API coverage ledger.
- Polished the Fortnox public docs after review: API coverage, command reference, references, and jobs/batches now use clearer public-ready wording without changing shipped behavior.

### Fixed
- CLI template: ensure argument/usage errors in `--output json` mode emit exactly one JSON error object (no argparse usage text).
- Clarified the engineering notes so the original `373` REST-operation lock stays historical while the current rendered-doc coverage lock remains `377`, and added a docs consistency test to guard that wording.
- Fixed a stale command-reference contradiction that said action-like Fortnox GET flows were unshipped even though invoice, offer, and order preview/print/send commands are shipped with explicit safety handling.

### Removed
