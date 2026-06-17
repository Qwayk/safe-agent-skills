# Proof and verification

This page shows what has actually been checked for the Fortnox skill so far. It answers whether the mapped commands, safety rules, docs, examples, and local tests agree with each other before anyone uses the skill on a real Fortnox account. The local code and tests are strong, but the latest validation did not have live Fortnox credentials, so live production checks remain honestly unverified here.

If you only check one thing, check the latest local test result and the live-unverified notes before asking the agent to plan any change that could affect invoices, supplier bills, bookkeeping, payroll, or stock.

## Last verified

- Date (UTC): `2026-06-17`
- Tool version: `0.1.0`
- Provider boundary: Fortnox REST base `https://api.fortnox.se/3` plus websocket stream `wss://ws.fortnox.se/topics-v1`
- Verification method: official-doc mapping plus local unit tests

## Local verification

Verified commands:

- `python3 -m venv .venv`
- `.venv/bin/python -m pip install -e .`
- `.venv/bin/python -m unittest -q`

Latest result:

- `Ran 669 tests in 77.559s, OK.`

Standards and packaging validation:

- New-tool flow audit passed.
- Control-room audit passed.
- Project standards audit passed.
- The Fortnox scoped whitespace check returned no issues.
- The live-ready public clone tests passed before the docs patch was pushed to GitHub.

Attachment-focused validation:

- `.venv/bin/python -m unittest -q tests.test_attachment`
- `Ran 8 tests, OK.`

Fortnox Finans validation:

- `.venv/bin/python -m unittest -q tests.test_fortnox_finans`
- `Ran 8 tests, OK.`

Integration Sales validation:

- `.venv/bin/python -m unittest -q tests.test_integration_sales`
- `Ran 3 tests, OK.`

Article URL connections family validation:

- `.venv/bin/python -m unittest -q tests.test_remaining_reads`
- `Ran 13 tests, OK.`

Coverage-lock alignment validation:

- `.venv/bin/python -m unittest -q tests.test_rest_inventory tests.test_coverage_alignment tests.test_remaining_reads`
- `Ran 21 tests, OK.`

Final REST coverage alignment validation:

- `.venv/bin/python -m unittest -q tests.test_rest_inventory tests.test_coverage_alignment`
- `Ran 8 tests, OK.`

Websocket coverage and command validation:

- `.venv/bin/python -m unittest -q tests.test_websocket_inventory tests.test_ws tests.test_rest_inventory tests.test_coverage_alignment`
- `Ran 18 tests, OK.`

Articles time-reporting read validation:

- `.venv/bin/python -m unittest -q tests.test_articles tests.test_rest_inventory tests.test_coverage_alignment`
- `Ran 23 tests, OK.`

Accounting read-filter validation:

- `.venv/bin/python -m unittest -q tests.test_accounting_reads`
- `Ran 18 tests, OK.`

Document PDF output validation:

- `.venv/bin/python -m unittest -q tests.test_api_runtime tests.test_document_outputs tests.test_rest_inventory tests.test_coverage_alignment`
- `Ran 19 tests, OK.`

Document delivery-action validation:

- `.venv/bin/python -m unittest -q tests.test_invoices tests.test_offers tests.test_orders`
- `Ran 28 tests, OK.`

## What is already proved

- `docs/api_coverage.md` accounts for the current official rendered Fortnox surface with `377` REST operations.
- The rendered official REST docs currently collapse into `79` explicit CLI families after repeated official labels are merged.
- The official websocket surface is accounted for with `19` topics and `60` documented events.
- `docs/api_coverage.md` now marks all `377` documented REST operations as shipped locally.
- `docs/api_coverage.md`, `src/fortnox_api_tool/_vendor/rest_inventory.json`, and `src/fortnox_api_tool/_vendor/websocket_inventory.json` are aligned and checked by local tests.
- High-risk no-snapshot applies are now covered by local refusal tests before any HTTP call on:
  - the shared request-layer contract
  - asset preflight state actions
  - contract preflight state actions
- The public README, quickstart, safety docs, and Fortnox skill wrapper are covered by local contract tests.
- `jobs run` is now honestly marked unsupported until real registry-backed Fortnox batch rows exist.
- The auth foundation is now implemented and covered by local tests for:
  - auth login URL generation and state-file handling
  - authorization-code exchange
  - refresh-token renewal and rotation-safe local storage
  - service-account client-credentials token fetch
  - live `/me` auth-check wiring
- The shipped accounting read slice is covered by local command-wiring tests:
  - account charts
  - accounts
  - article file connections
  - asset file connections
  - asset types
  - assets
  - archive
  - company information
  - company settings
  - custom document types
  - custom inbound documents
  - custom outbound documents
  - customers
  - email senders
  - inbox
  - manual documents
  - manual inbound documents
  - manual outbound documents
  - suppliers
  - articles
  - price lists
  - prices
  - projects
  - currencies
  - cost centers
  - terms of deliveries
  - terms of payments
  - financial years
  - predefined accounts
  - predefined voucher series
  - modes of payments
  - voucher series
  - vouchers
  - invoice payments
  - invoice accruals
  - supplier invoice accruals
  - supplier-invoice-payments
  - supplier invoice file connections
  - invoices
  - offers
  - orders
  - voucher file connections
- The shipped article, customer, and supplier list reads now keep their rendered Fortnox query/filter names explicit on the CLI.
- The rendered price-list list/get docs do not show extra query parameters, and the shipped CLI keeps those reads path-only.
- The shipped invoice, offer, and order PDF output block is covered by local command-wiring tests for:
  - `invoices preview|print|print-reminder`
  - `offers preview|print`
  - `orders preview|print`
  - PDF reads stay read-only
  - the CLI returns base64 in JSON output by default and writes the raw PDF bytes when `--output-file` is given
- The shipped invoice, offer, and order delivery-action block is covered by local command-wiring tests for:
  - `invoices send-an-invoice-as-e-invoice`
  - `invoices send-an-invoice-as-e-print`
  - `invoices send-an-invoice-as-email`
  - `offers send-given-offer-as-email`
  - `orders send-given-order-as-email`
  - all five keep the official GET method and the documented `DocumentNumber` path selector
  - apply stays dry-run by default and verifies success by read-back `Sent == true`
- The shipped websocket block is covered by local runtime and command-wiring tests for:
  - `ws tenants add`
  - `ws tenants remove`
  - `ws tenants list`
  - `ws topics add`
  - `ws subscribe start`
  - tenant add keeps the official `includeChildTenants`, `clientSecret`, and `accessTokens` payload shape
  - tenant remove keeps the official numeric `tenants` array payload
  - topic add keeps the documented optional topic replay offsets
  - subscribe opens one connection, sends the official `add-tenants-v1`, then `add-topics-v1`, then `subscribe-v1`, and collects event messages until the configured stop rule
  - command output redacts websocket access tokens and client secrets
- The shipped `articles` family now also covers the time-reporting article-registration read:
  - `list`
  - `get`
  - `list-time-article-registrations`
  - `create`
  - `update`
  - `delete`
  - `list-time-article-registrations` keeps the official plural filter names explicit: `customerIds`, `projectIds`, `itemIds`, `costCenterIds`, and `ownerIds`
  - the time-reporting endpoint keeps the official camelCase boolean filters explicit
  - the time-reporting success body is handled honestly as a JSON array instead of being forced into an object shape
- The shipped wrapped file-connections block is covered by local command-wiring and plan/apply tests for:
  - `article-file-connections list|get|create|remove`
  - `supplier-invoice-file-connections list|get|create|remove`
  - `voucher-file-connections list|get|create|remove`
  - list commands keep the documented Fortnox query names explicit on the CLI
  - create commands require the documented top-level wrapper object and verify by follow-up item GET on `FileId`
  - remove commands require `--yes --ack-irreversible` and verify absence by follow-up item GET
- The shipped supplier-invoice external-url-connections slice is covered by local command-wiring and plan/apply tests for:
  - `get`
  - `create`
  - `update`
  - `remove`
  - `create` and `update` keep the documented flat request body instead of inventing a wrapper
  - create verifies by resolved response `Id` plus follow-up GET
  - remove requires `--yes --ack-irreversible` and verifies absence by follow-up GET
  - the rendered docs note create starts inactive until a supplier-invoice file connection exists, and the CLI keeps that behavior as documentation rather than fabricating extra activation logic
- The shipped Fortnox Finans block is covered by local command-wiring and plan/apply tests for:
  - `get`
  - `send-an-invoice-with-fortnox-finans`
  - `action-pause`
  - `action-report-payment`
  - `action-stop`
  - create and all five documented actions are dry-run by default
  - create plus all five documented actions require `--yes` on apply because the official docs warn they can trigger real finance processing
  - create uses the documented `NoxFinansInvoice` wrapper and verifies by follow-up GET on `InvoiceNumber`
  - `pause` and `report-payment` keep the documented wrapper payloads
  - `stop` keeps the documented no-body path unless the user explicitly supplies a reviewed wrapper payload
  - follow-up verification stays on GET because the rendered docs do not clearly pin one stable post-action state field for every Fortnox Finans action
- The shipped Integration Sales block is covered by local command-wiring tests for:
  - `get-by-app-id`
  - `get-by-app-id-and-tenant`
  - `resolves-sales-information-of-an-integration`
  - all three commands keep the official GET paths explicit
  - the two integration-partner endpoints stay documented as deprecated, matching the rendered Fortnox docs
- The shipped remaining small-read sweep is covered by local command-wiring tests for:
  - `eu-vat-limit-regulation get`
  - `integration-ratings list`
  - `sie get`
  - `stock-status get-stock-balance`
  - `tenant get`
  - `users fetch-user-information-for-a-single-published-integration-and-tenant`
  - `sie get` keeps the official streamed/octet-stream success path as plain text output instead of forcing JSON parsing
  - `stock-status get-stock-balance` keeps the documented comma-separated `itemIds` and `stockPointCodes` filters explicit on the CLI
- The shipped `article-url-connections` family is covered by local command-wiring and plan/apply tests for:
  - `list`
  - `get`
  - `create`
  - `update`
  - `delete`
  - create and update keep the official wrapped `ArticleUrlConnection` payload
  - create and update verify by follow-up GET on the documented `Id` path
  - delete requires `--yes --ack-irreversible` and verifies absence by follow-up GET
- The shipped purchase-orders block is covered by local command-wiring and plan/apply tests for:
  - `list|get|get-csv|get-note`
  - `create|update|partial-update-purchase-order`
  - `manually-complete-purchase-order`
  - `sends-multiple-purchase-orders-via-email`
  - `update-response-bulk`
  - `void`
  - raw warehouse payload validation rejects stale wrapper-style payloads
  - CSV reads keep the raw text response instead of forcing JSON parsing
  - manual complete handles the documented `204` response and verifies by follow-up GET
  - bulk send uses repeated `--id` selectors for the documented raw id array
  - bulk response-state update uses the documented `ids` query parameter and verifies every target by read-back GET
- The shipped incoming-goods block is covered by local command-wiring and plan/apply tests for:
  - `list|get`
  - `create|update|partial-update-incoming-goods-document`
  - `complete-incoming-goods-document`
  - `release`
  - `void`
  - raw warehouse payload validation rejects stale wrapper-style payloads
  - create verifies by resolved response `id` plus read-back GET
  - complete sends the documented raw JSON string bookkeeping date and handles the documented `204` response
  - release and void handle the documented `204` responses and verify by follow-up GET
- The shipped stock-points block is covered by local command-wiring and plan/apply tests for:
  - `list|get|get-stock-locations|list-multi`
  - `create|update`
  - `append-stock-locations`
  - `delete`
  - raw warehouse payload validation rejects stale wrapper-style stock-location arrays on `append-stock-locations`
  - create verifies by resolved response `id` plus read-back GET
  - update verifies selected read-back fields on the returned stock point
  - `append-stock-locations` verifies appended location codes by follow-up stock-location GET
  - delete requires the documented irreversible confirmation and verifies absence after apply
- The shipped stock-taking block is covered by local command-wiring and plan/apply tests for:
  - `list|get|get-candidate-rows|get-rows`
  - `create|update`
  - `add-rows|add-rows-by-filter`
  - `delete|delete-row|delete-rows`
  - `release|void`
  - raw warehouse payload validation rejects stale wrapper-style row payloads on `add-rows`
  - create verifies by resolved response `id` plus read-back GET
  - update verifies the expected `state` when that field is present in the payload
  - row-write flows verify row presence or absence by follow-up row GET
  - delete paths require the documented irreversible confirmation and verify absence after apply
  - `release` and `void` handle the documented state-changing warehouse paths and verify `completed` and `voided` by follow-up GET
- The shipped stock-transfers block is covered by local command-wiring and plan/apply tests for:
  - `get`
  - `create|update`
  - `release|void`
  - raw warehouse payload validation rejects stale wrapper-style payloads
  - create verifies by resolved response `id` plus follow-up GET
  - update validates raw payload `id` against `--id` when present and verifies by follow-up GET
  - `release` requires `--yes` and `void` requires `--yes --ack-irreversible`
  - `release` and `void` handle the documented stock-transfer action paths and verify by follow-up GET
- The shipped production-orders block is covered by local command-wiring and plan/apply tests for:
  - `list|get|get-bill-of-materials`
  - `create|update|update-note`
  - `release|void`
  - raw warehouse payload validation rejects stale wrapper-style payloads
  - create verifies by resolved response `id` plus follow-up GET
  - update and update-note validate raw payload `id` against `--id` when present and verify by follow-up GET
  - `release` requires `--yes` and `void` requires `--yes --ack-irreversible`
  - `release` and `void` handle the documented production-order action paths and verify by follow-up GET
- The shipped document-intake read block is covered by local command-wiring tests for:
  - `archive get-root|get-file`
  - `inbox get-root|get-file`
  - `custom-document-types list|get`
  - `custom-inbound-documents get`
  - `custom-outbound-documents get`
- The shipped helper accounting block is covered by local command-wiring tests for:
  - `customer-references list|get|create|update|delete`
  - `expenses list|get|create`
  - `tax-reductions list|get|create|update|remove`
  - `labels list|create|update|delete`
  - `locked-period get`
  - `print-templates list`
  - `manual-documents list`
  - `manual-inbound-documents get`
  - `manual-outbound-documents get`
  - `email-senders list`
  - `archive get-root` also checks the documented `path` and `fileid` query wiring
- The shipped document-intake write block is covered by local plan/apply tests for:
  - `archive delete|remove|upload-a-file-to-a-specific-subdirectory`
  - `custom-document-types create`
  - `custom-inbound-documents save|release|void`
  - `custom-outbound-documents save|release|void`
  - `inbox remove|upload-a-file`
  - `manual-inbound-documents create|update-note`
  - `manual-outbound-documents release`
  - `email-senders add-a-new-email-address-as-trusted|delete`
  - create and save flows emit dry-run plans and re-check payload hashes on apply
  - archive and inbox uploads use multipart `file` upload wiring and verify by read-back GET on the returned file `Id`
  - archive remove requires explicit `--path` so the target stays narrow
  - release flows require `--yes`
  - archive delete, archive remove, inbox remove, and void flows require `--yes --ack-irreversible`
  - manual note updates verify the note by read-back
  - trusted-sender add and delete verify by follow-up list lookup
- The shipped attachment block is covered by local command-wiring and plan/apply tests for:
  - `get`
  - `list`
  - `attach-files-to-one-or-more-entities`
  - `detach-file`
  - `update`
  - `validates-a-list-of-attachments-that-will-be-included-on-send`
  - `get` and `list` wire the documented repeated `entityid`/`entityids` query params
  - `attach` and `update` use the documented JSON array/object shapes and verify by follow-up GET
  - `detach-file` requires `--yes --ack-irreversible` and stays honest with response-only verification because the rendered docs here do not show a documented GET-by-attachment-id follow-up
  - `validates-a-list-of-attachments-that-will-be-included-on-send` posts the documented JSON array without a write plan
- The shipped bookkeeping write slice is covered by local plan/apply tests for:
  - `financial-years create`
  - `predefined-accounts update`
  - `predefined-voucher-series update`
  - `vouchers create`
  - each write uses a reviewed `--plan-in`
  - `vouchers create` verifies by read-back GET on the voucher series and number pair, using `--financial-year` when applicable
- The shipped fixed-assets block is covered by local plan/apply tests for:
  - `asset-file-connections create|remove`
  - `asset-types create|update|delete`
  - `assets create|update|delete`
  - `assets change-manual-ob-value-of-an-asset`
  - `assets perform-a-depreciation-of-an-asset`
  - `assets scrap-an-asset|sell-an-asset|write-down-an-asset|write-up-an-asset`
  - `asset-file-connections remove`, `asset-types delete`, and `assets delete|scrap-an-asset|sell-an-asset` require `--yes --ack-irreversible`
  - the remaining shipped asset lifecycle actions require `--yes`
  - asset CRUD verifies by read-back GET, asset-file-connections verifies by follow-up list scan on `FileId`, and depreciation verifies by the documented response rows
- The shipped invoice-payment write slice is covered by local plan/apply tests for:
  - create dry-run plan emission
  - update dry-run plan emission
  - bookkeep dry-run plan emission
  - payload-hash drift refusal on apply for create, update, and bookkeep
  - create apply with read-back verification
  - update apply with read-back verification
  - update and bookkeep number-mismatch validation
  - remove refusal without `--yes`
  - remove refusal without irreversible acknowledgement
  - remove apply plus absence verification
  - bookkeep refusal without `--yes`
  - bookkeep apply with `Booked=true` verification
  - bookkeep verification-failure handling when `Booked` stays `false`
- The shipped invoice-accrual CRUD slice is covered by local plan/apply tests for:
  - dry-run plan emission
  - payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update apply plus read-back verification
  - remove refusal without irreversible acknowledgement
  - remove apply plus absence verification
- The shipped contract-accrual CRUD slice is covered by local plan/apply tests for:
  - list and get read calls
  - dry-run plan emission
  - payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update selector mismatch validation
  - update apply plus read-back verification
  - remove refusal without `--yes`
  - remove refusal without `--ack-irreversible`
  - remove apply plus absence verification
- The shipped contract-template write slice is covered by local plan/apply tests for:
  - list and get read calls
  - dry-run plan emission
  - payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update selector mismatch validation
  - update apply plus read-back verification
- The shipped contracts read/write/action slice is covered by local plan/apply tests for:
  - list query-parameter wiring for the documented Fortnox filters
  - get read calls
  - create dry-run plan emission
  - create payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update selector mismatch validation
  - `create-invoice` apply with optional `--invoice-date` query wiring and before/after verification
  - `increase-invoice-count` apply with `InvoicesRemaining` increase verification
  - `finish` apply failure handling when `Active` stays `true`
- The shipped supplier-invoice-payment write slice is covered by local plan/apply tests for:
  - dry-run plan emission
  - payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update apply plus read-back verification
  - update and bookkeep number-mismatch validation
  - remove refusal without `--yes`
  - remove refusal without irreversible acknowledgement
  - remove apply plus absence verification
  - bookkeep refusal without `--yes`
  - bookkeep apply with `Booked=true` verification
  - bookkeep verification-failure handling when `Booked` stays `false`
- The shipped supplier-invoices read/write slice is covered by local plan/apply tests for:
  - list and get read calls
  - create dry-run plan emission
  - update dry-run plan emission
  - payload-hash drift refusal on create and update apply
  - create and update apply plus read-back verification
  - update number-mismatch validation
- The shipped supplier-invoices action slice is covered by local plan/apply tests for:
  - `approvalbookkeep` dry-run with optional payload
  - `bookkeep` dry-run plus apply with `Booked == true` verification
  - `bookkeep` apply verification failure when `Booked` remains `false`
  - `approvalpayment` apply plus `PaymentPending == false` verification
  - `cancel` apply plus `Cancelled == true` verification
  - `credit` apply plus `Credit == true` and present `CreditReference` verification
- The shipped accounts write slice is covered by local plan/apply tests for:
  - `create` dry-run plan emission
  - `create` and `update` payload-hash drift refusal on apply
  - `create` and `update` apply plus read-back verification
  - `update` payload number mismatch validation
  - `delete` dry-run plan emission
  - `delete` refusal without `--yes`
  - `delete` refusal without `--ack-irreversible`
  - `delete` apply plus absence verification
- The shipped offers write slice is covered by local plan/apply tests for:
  - `create` and `update` dry-run plan emission
  - create and update read-back verification
  - `update` payload number mismatch validation
  - `cancel` dry-run plan emission
  - `cancel` payload-hash safety checks
  - `cancel` apply with identifier validation and read-back confirmation
  - `create-invoice`, `create-order`, and `externalprint` dry-run plan emission
  - action-style write endpoints apply with reviewed `--plan-in --yes` and read-back confirmation
- The shipped orders write slice is covered by local plan/apply tests for:
  - `create` and `update` dry-run plan emission
  - create and update read-back verification
  - `update` payload number mismatch validation
  - `cancel` dry-run plan emission
  - `cancel` payload hash and identifier safety checks
  - `cancel` apply with read-back confirmation
  - `create-invoice` and `externalprint` dry-run plan emission
  - action-style write endpoints apply with reviewed `--plan-in --yes` and read-back confirmation
- The shipped invoices write slice is covered by local plan/apply tests for:
  - `create` and `update` dry-run plan emission
  - create and update read-back verification
  - `update` payload number mismatch validation
  - `bookkeep`, `cancel`, `credit`, `warehouseready`, and `externalprint` dry-run plan emission
  - action-style write endpoints apply with reviewed `--plan-in --yes`
  - `bookkeep` and `cancel` state checks by read-back confirmation
- The shipped customers write slice is covered by local plan/apply tests for:
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` create response number fallback verification
  - `create` fail-safe when no `CustomerNumber` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload number mismatch validation
  - `delete` dry-run plan emission
  - `delete` refusal without `--yes`
  - `delete` refusal without `--ack-irreversible`
  - `delete` apply plus absence verification
- The shipped suppliers write slice is covered by local plan/apply tests for:
  - top-level `Supplier` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` create response number fallback verification
  - `create` fail-safe when no `SupplierNumber` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload number mismatch validation
- The shipped employees read/write slice is covered by local tests for:
  - `list` and `get` command wiring
  - top-level `Employee` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `EmployeeId` verification fallback
  - `create` fail-safe when no `EmployeeId` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` path and payload `EmployeeId` mismatch validation
- The shipped payroll/time block is covered by local tests for:
  - `absence-transactions list|get|get-by-employee-date-code|create|update|delete`
  - `attendance-transactions list|get|get-by-employee-date-code|create|update|delete`
  - `salary-transactions list|get|create|update|delete`
  - `schedule-times get|update|reset-day`
  - `registrations get`
  - `vacation-debt-basis get`
  - top-level wrapper validation for `AbsenceTransaction`, `AttendanceTransaction`, `SalaryTransaction`, and `ScheduleTime`
  - create dry-run plan emission plus payload-hash drift refusal on apply
  - read-back verification for absence, attendance, salary, and schedule-time writes
  - irreversible delete confirmation and absence verification for absence, attendance, and salary transactions
  - path/payload selector enforcement for `SalaryTransaction.SalaryRow` and `ScheduleTime.EmployeeId` plus `ScheduleTime.Date` when present
  - official `/api/time/registrations-v2` runtime handling without breaking the normal Fortnox `/3` base URL contract
- The shipped articles write slice is covered by local plan/apply tests for:
  - top-level `Article` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `ArticleNumber` verification fallback
  - `create` fail-safe when no `ArticleNumber` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload number mismatch validation
  - `delete` dry-run plan emission
  - `delete` refusal without `--yes`
  - `delete` refusal without `--ack-irreversible`
  - `delete` apply plus absence verification
- The shipped price-lists write slice is covered by local plan/apply tests for:
  - top-level `PriceList` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response `Code` fallback verification
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload code mismatch validation
- The shipped prices write slice is covered by local plan/apply tests for:
  - top-level `Price` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload composite-key verification fallback
  - `create` fail-safe when the composite key cannot be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` selector mismatch validation for `PriceList` and `ArticleNumber`
  - `update-by-from-quantity` dry-run plan emission
  - `update-by-from-quantity` apply plus read-back verification
  - `update-by-from-quantity` selector mismatch validation for `FromQuantity`
  - `delete` dry-run plan emission
  - `delete` refusal without `--yes`
  - `delete` refusal without `--ack-irreversible`
  - `delete` apply plus absence verification
- The shipped terms-of-deliveries write slice is covered by local plan/apply tests for:
  - top-level `TermsOfDelivery` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload code mismatch validation
- The shipped terms-of-payments write slice is covered by local plan/apply tests for:
  - top-level `TermsOfPayment` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload code mismatch validation
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped units read/write/remove slice is covered by local tests for:
  - `list` and `get` command wiring
  - top-level `Unit` wrapper validation on input and outbound write payloads
  - `create` and `update` dry-run plan emission
  - `create` and `update` payload-hash drift refusal on apply
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` apply plus read-back verification
  - `update` path and payload `Code` mismatch validation
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped projects write slice is covered by local plan/apply tests (`tests.test_projects = 14`) for:
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped modes-of-payments write slice is covered by local plan/apply tests (`tests.test_modes_of_payments = 14`) for:
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped voucher-series write slice is covered by local plan/apply tests (`tests.test_voucher_series = 9`) for:
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
- The shipped way-of-deliveries read/write/remove slice is covered by local tests for:
  - `list` and `get` command wiring
  - top-level `WayOfDelivery` wrapper validation on input and outbound write payloads
  - `create` and `update` dry-run plan emission
  - `create` and `update` payload-hash drift refusal on apply
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` apply plus read-back verification
  - `update` path and payload `Code` mismatch validation
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped cost-centers write slice is covered by local plan/apply tests for:
  - top-level `CostCenter` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload code mismatch validation
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped currencies write slice is covered by local plan/apply tests for:
  - top-level `Currency` wrapper validation on input and outbound write payloads
  - `create` dry-run plan emission
  - `create` payload-hash drift refusal on apply
  - `create` apply plus read-back verification
  - `create` response-or-payload `Code` verification fallback
  - `create` fail-safe when no `Code` can be resolved for verification
  - `update` dry-run plan emission
  - `update` payload-hash drift refusal on apply
  - `update` apply plus read-back verification
  - `update` payload code mismatch validation
  - `remove` dry-run plan emission
  - `remove` refusal without `--yes`
  - `remove` refusal without `--ack-irreversible`
  - `remove` apply plus absence verification
- The shipped supplier-invoice-accrual CRUD slice is covered by local plan/apply tests for:
  - dry-run plan emission
  - payload-hash drift refusal on apply
  - create apply plus read-back verification
  - update apply plus read-back verification
  - remove refusal without irreversible acknowledgement
  - remove apply plus absence verification
- The coverage-lock alignment itself is now covered by local tests for:
  - `docs/api_coverage.md` versus the vendored REST inventory rows
  - `docs/api_coverage.md` versus the vendored websocket inventory rows
  - shared audited-date alignment across the coverage doc and both inventories

## What is still live-unverified

- No live Fortnox request has been run from this workspace with real credentials yet.
- No live Fortnox write workflow has been run from this workspace yet.
- No websocket stream connection has been run from this workspace yet.
- The full documented REST and websocket surface is shipped locally, but all live Fortnox verification is still pending from this workspace.

## Live-proof checklist for the next run

- On `2026-06-17`, this validation copy did not contain a local `.env`, `.state/token.json`, or `.state/oauth_state.json` with real Fortnox credentials.
- Before any live check, run onboarding and fill the real Fortnox app values for `FORTNOX_CLIENT_ID`, `FORTNOX_CLIENT_SECRET`, and `FORTNOX_REDIRECT_URI`.
- Then run one real auth proof:
  - `fortnox-api-tool auth login`
  - `fortnox-api-tool auth exchange-code --code <authorization_code> --state <saved_state>`
  - `fortnox-api-tool auth check`
- Then run one safe real REST read:
  - `fortnox-api-tool company-information get`
- Then run one small websocket proof with the documented websocket tenant access token and client secret:
  - `fortnox-api-tool ws subscribe start --topic invoices --max-events 1 --idle-timeout-s 5`
- If credentials are still unavailable, keep the public claim at: fully shipped locally, live-unverified from this workspace.

## Example outputs

These example files are representative redacted docs examples only. They show output shapes and safe wording, but they are not live Fortnox proof captured from this workspace.

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/outputs/ws_subscribe_start.json`

## Important note

The direct OpenAPI download linked from `https://api.fortnox.se/apidocs` returned HTTP `429` from this environment on `2026-06-09`, so the current coverage lock was extracted from the rendered official docs page instead.

## Links

- Source list: `docs/references.md`
- Coverage ledger: `docs/api_coverage.md`
