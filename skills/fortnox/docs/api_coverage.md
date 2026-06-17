# API coverage

Last audited (UTC): 2026-06-16

Fortnox coverage shows exactly what this skill can do with company details, customers, suppliers, invoices, supplier invoices, bookkeeping, payroll, time, stock, attachments, documents, websocket topics, and careful change plans. It also shows which commands are shipped and which behavior still needs real Fortnox credentials before it can be called live-verified.

Read the mapped command rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether this skill can inspect Fortnox company details, customers, invoices, supplier bills, and stock, then show which changes need a reviewed plan."

## Totals

- Official REST operations accounted for: `377`
- Rendered REST tag count from official docs: `81`
- Unique REST CLI family slugs after merging repeated official labels: `79`
- Official websocket control commands accounted for: `5`
- Official websocket topics accounted for: `19`
- Official websocket events accounted for: `60`
- Shipped explicit REST commands today: `377`
- Shipped explicit websocket commands today: `24`
- Current stage: coverage lock is complete, the auth foundation is shipped, and every currently mapped official REST and websocket operation has a local CLI command path. That still does not justify a blanket completeness claim: live verification is still pending from this workspace, and all rendered-doc behavior remains honestly marked live-unverified until real Fortnox credentials are used here.

## Source notes

- REST source: `https://api.fortnox.se/apidocs`
- Websocket source: `https://www.fortnox.se/developer/guides-and-good-to-know/websockets`
- Official OpenAPI download is linked from the docs page, but direct download returned HTTP 429 from this environment on 2026-06-09.
- This inventory is derived from the rendered official docs page itself and kept as the current coverage-lock record.
- The official docs repeat the labels `Articles` and `Integration Sales`; this ledger merges those repeated labels by CLI family slug so planned commands stay unique.

## REST group summary

| Group | Families | Operations | Notes |
|---|---:|---:|---|
| `Developer` | 1 | 3 | Official integration sales endpoints marked deprecated in the docs. |
| `fileattachments` | 1 | 6 | Official file attachment REST surface. |
| `fortnox` | 60 | 281 | Main Fortnox REST business surface. |
| `integration-developer` | 2 | 2 | Official integration-developer helper endpoints. |
| `time-reporting` | 2 | 2 | Official time-reporting REST surface. |
| `warehouse` | 14 | 83 | Warehouse and stock-document REST surface. |

## REST family summary

| Family | Official labels | Operations | Planned CLI prefix | Ship status | Notes |
|---|---|---:|---|---|---|
| `absence-transactions` | `Absence Transactions` | 6 | `fortnox-api-tool absence-transactions` | Shipped | All documented operations are shipped with plan-first writes, delete confirmation, read-back verification, and the extra employee/date/code GET. |
| `account-charts` | `Account Charts` | 1 | `fortnox-api-tool account-charts` | Shipped | Read-only `list` is shipped. |
| `accounts` | `Accounts` | 5 | `fortnox-api-tool accounts` | Shipped | All documented operations are shipped. |
| `archive` | `Archive` | 5 | `fortnox-api-tool archive` | Shipped | All documented operations are shipped with plan-first upload, explicit path targeting for `remove`, and irreversible delete confirmation. |
| `article-file-connections` | `Article File Connections` | 4 | `fortnox-api-tool article-file-connections` | Shipped | All documented operations are shipped with plan-first create and irreversible remove verification via follow-up GET. |
| `article-url-connections` | `Article Url Connections` | 5 | `fortnox-api-tool article-url-connections` | Shipped | All documented operations are shipped with plan-first create, update, and delete flows plus follow-up GET or absence verification. |
| `articles` | `Articles` | 6 | `fortnox-api-tool articles` | Shipped | The CRUD and time-reporting GET commands are wired locally. Official docs render the Articles tag twice; this ledger merges both rendered tags into one CLI family. The rendered article list filters are now shipped explicitly on the CLI. |
| `asset-file-connections` | `fortnox_AssetFileConnection` | 3 | `fortnox-api-tool asset-file-connections` | Shipped | All documented operations are shipped with plan-first create and irreversible remove verification via follow-up list checks. |
| `asset-types` | `Asset Types` | 5 | `fortnox-api-tool asset-types` | Shipped | All documented operations are shipped with plan-first writes, path-id enforcement on update, and read-back or absence verification. |
| `assets` | `Assets` | 12 | `fortnox-api-tool assets` | Shipped | All documented operations are shipped with plan-first writes, explicit `--yes` safety for lifecycle actions, irreversible protection for `delete`, `scrap`, and `sell`, read-back verification for CRUD and state changes, and response-row verification for depreciation. |
| `attachment` | `Attachment` | 6 | `fortnox-api-tool attachment` | Shipped | All documented operations are shipped with plan-first writes where applicable, explicit detach confirmation, and follow-up read or response verification. |
| `attendance-transactions` | `Attendance Transactions` | 6 | `fortnox-api-tool attendance-transactions` | Shipped | All documented operations are shipped with plan-first writes, delete confirmation, read-back verification, and the extra employee/date/code GET. |
| `company-information` | `Company Information` | 1 | `fortnox-api-tool company-information` | Shipped | Read-only `get` is shipped. |
| `company-settings` | `Company Settings` | 1 | `fortnox-api-tool company-settings` | Shipped | Read-only `get` is shipped. |
| `contract-accruals` | `Contract Accruals` | 5 | `fortnox-api-tool contract-accruals` | Shipped | All documented operations are shipped with plan-first writes, selector checks, and read-back verification. |
| `contract-templates` | `Contract Templates` | 4 | `fortnox-api-tool contract-templates` | Shipped | All documented operations are shipped with plan-first writes and read-back verification. |
| `contracts` | `Contracts` | 7 | `fortnox-api-tool contracts` | Shipped | All documented operations are shipped with plan-first writes, documented list filters, and action-specific verification. |
| `cost-centers` | `Cost Centers` | 5 | `fortnox-api-tool cost-centers` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |
| `currencies` | `Currencies` | 5 | `fortnox-api-tool currencies` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |
| `custom-document-types` | `Custom Document Type` | 3 | `fortnox-api-tool custom-document-types` | Shipped | All documented operations are shipped with plan-first create verification. |
| `custom-inbound-documents` | `Custom Inbound Document` | 4 | `fortnox-api-tool custom-inbound-documents` | Shipped | All documented operations are shipped with plan-first save/release/void flows and read-back verification. |
| `custom-outbound-documents` | `Custom Outbound Document` | 4 | `fortnox-api-tool custom-outbound-documents` | Shipped | All documented operations are shipped with plan-first save/release/void flows and read-back verification. |
| `customer-references` | `Customer References` | 5 | `fortnox-api-tool customer-references` | Shipped | All documented operations are shipped with plan-first writes and read-back verification. |
| `customers` | `Customers` | 5 | `fortnox-api-tool customers` | Shipped | All documented operations are wired locally, including the rendered customer list filters. |
| `email-senders` | `Email Senders` | 3 | `fortnox-api-tool email-senders` | Shipped | All documented operations are shipped with plan-first trusted-sender add and delete verification. |
| `employees` | `Employees` | 4 | `fortnox-api-tool employees` | Shipped | `list`, `get`, `create`, and `update` are fully shipped with plan-first writes and verification. |
| `eu-vat-limit-regulation` | `EU Vat Limit Regulation` | 1 | `fortnox-api-tool eu-vat-limit-regulation` | Shipped | Read-only `get` is shipped with the documented optional `year` query filter kept explicit. |
| `expenses` | `Expenses` | 3 | `fortnox-api-tool expenses` | Shipped | All documented operations are shipped with plan-first create and read-back verification. |
| `financial-years` | `Financial Years` | 3 | `fortnox-api-tool financial-years` | Shipped | All documented operations are shipped. |
| `fortnox-finans` | `Fortnox Finans` | 7 | `fortnox-api-tool fortnox-finans` | Shipped | All documented operations are shipped with plan-first writes, explicit `--yes` confirmation on apply, and follow-up GET verification. |
| `inbox` | `Inbox` | 4 | `fortnox-api-tool inbox` | Shipped | All documented operations are shipped with plan-first upload and irreversible remove confirmation. |
| `incoming-goods` | `Incoming Goods` | 8 | `fortnox-api-tool incoming-goods` | Shipped | All documented incoming-goods operations are shipped with raw warehouse payloads, plan-first writes, `--id` selectors, a raw JSON string bookkeeping date for complete, and follow-up state verification for actions. |
| `integration-ratings` | `Integration Ratings` | 1 | `fortnox-api-tool integration-ratings` | Shipped | Read-only `list` is shipped. |
| `integration-sales` | `Integration Sales` | 3 | `fortnox-api-tool integration-sales` | Shipped | All documented operations are shipped as read-only GET commands. Official docs render the Integration Sales tag twice; this ledger merges both rendered tags into one CLI family, and the two integration-partner endpoints are marked deprecated in the rendered docs. |
| `invoice-accruals` | `Invoice Accruals` | 5 | `fortnox-api-tool invoice-accruals` | Shipped | All documented invoice-accrual operations are shipped with plan-first writes and read-back verification. |
| `invoice-payments` | `Invoice Payments` | 6 | `fortnox-api-tool invoice-payments` | Shipped | All operations are shipped, including plan-first create/update/remove/bookkeep with verification. |
| `invoices` | `Invoices` | 15 | `fortnox-api-tool invoices` | Shipped | All documented operations are shipped. The preview, print, print-reminder, e-invoice, e-print, and email GET endpoints are treated honestly as document-output or delivery-triggering actions with explicit commands and safety checks. |
| `labels` | `Labels` | 4 | `fortnox-api-tool labels` | Shipped | The current rendered docs in this environment show the 4-operation labels surface; all four are shipped with plan-first writes and list-based verification. |
| `locked-period` | `Locked Period` | 1 | `fortnox-api-tool locked-period` | Shipped | All documented operations are shipped. |
| `manual-documents` | `Manual Document` | 1 | `fortnox-api-tool manual-documents` | Shipped | Read-only `list` is shipped. |
| `manual-inbound-documents` | `Manual Inbound Document` | 6 | `fortnox-api-tool manual-inbound-documents` | Shipped | All documented operations are shipped with plan-first create/update/update-note/release/void verification. |
| `manual-outbound-documents` | `Manual Outbound Document` | 6 | `fortnox-api-tool manual-outbound-documents` | Shipped | All documented operations are shipped with plan-first create/update/update-note/release/void verification. |
| `me` | `Me` | 1 | `fortnox-api-tool auth` | Shipped | `auth check` ships the official `/3/me` read for live token validation. |
| `modes-of-payments` | `Modes Of Payments` | 5 | `fortnox-api-tool modes-of-payments` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |
| `offers` | `Offers` | 11 | `fortnox-api-tool offers` | Shipped | All documented operations are shipped. The preview, print, and email GET endpoints are treated honestly as document-output or delivery-triggering actions with explicit commands and safety checks. |
| `orders` | `Orders` | 10 | `fortnox-api-tool orders` | Shipped | All documented operations are shipped. The preview, print, and email GET endpoints are treated honestly as document-output or delivery-triggering actions with explicit commands and safety checks. |
| `predefined-accounts` | `Pre Defined Accounts` | 3 | `fortnox-api-tool predefined-accounts` | Shipped | All documented operations are shipped. |
| `predefined-voucher-series` | `Predefined Voucher Series` | 3 | `fortnox-api-tool predefined-voucher-series` | Shipped | All documented operations are shipped. |
| `price-lists` | `Price Lists` | 4 | `fortnox-api-tool price-lists` | Shipped | All documented operations are wired locally with plan-first create and update verification. The current rendered price-list list/get docs do not show extra query filters. |
| `prices` | `Prices` | 8 | `fortnox-api-tool prices` | Shipped | All documented operations are shipped, including plan-first create, update, update-by-from-quantity, and delete verification. |
| `print-templates` | `Print Templates` | 1 | `fortnox-api-tool print-templates` | Shipped | All documented operations are shipped. |
| `production-orders` | `Production Order` | 8 | `fortnox-api-tool production-orders` | Shipped | All documented operations are shipped. |
| `projects` | `Projects` | 5 | `fortnox-api-tool projects` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |
| `purchase-orders` | `Purchase Order` | 15 | `fortnox-api-tool purchase-orders` | Shipped | All documented purchase-order operations are shipped with raw warehouse payloads, plan-first writes, `--id` selectors, CSV-safe reads, and follow-up state verification for actions. |
| `registrations` | `Registrations` | 1 | `fortnox-api-tool registrations` | Shipped | Read-only `get` is shipped against the official `/api/time/registrations-v2` endpoint. |
| `salary-transactions` | `Salary Transactions` | 5 | `fortnox-api-tool salary-transactions` | Shipped | All documented operations are shipped with plan-first writes, delete confirmation, and read-back verification. |
| `schedule-times` | `Schedule Times` | 3 | `fortnox-api-tool schedule-times` | Shipped | `get`, `update`, and `reset-day` are shipped with plan-first writes and read-back verification. |
| `sie` | `Sie` | 1 | `fortnox-api-tool sie` | Shipped | Read-only `get` is shipped and keeps the streamed SIE response as plain text output. |
| `stock-points` | `Stock Point` | 8 | `fortnox-api-tool stock-points` | Shipped | All documented stock-point operations are shipped with raw warehouse payloads, explicit state/read filters, and follow-up verification for create, update, append, and delete. |
| `stock-status` | `Stock Status` | 1 | `fortnox-api-tool stock-status` | Shipped | Read-only `get-stock-balance` is shipped with explicit itemIds and stockPointCodes filters. |
| `stock-taking` | `Stock Taking` | 13 | `fortnox-api-tool stock-taking` | Shipped | All documented stock-taking operations are shipped with raw warehouse payloads, explicit row/filter commands, plan-first writes, and follow-up verification for row changes and state changes. |
| `stock-transfers` | `Stock Transfer` | 5 | `fortnox-api-tool stock-transfers` | Shipped | All documented operations are shipped. |
| `supplier-invoice-accruals` | `Supplier Invoice Accruals` | 5 | `fortnox-api-tool supplier-invoice-accruals` | Shipped | All documented supplier-invoice-accrual operations are shipped with plan-first writes and read-back verification. |
| `supplier-invoice-external-url-connections` | `Supplier Invoice External Url Connections` | 4 | `fortnox-api-tool supplier-invoice-external-url-connections` | Shipped | All documented operations are shipped with plan-first writes, `Id`-based read-back verification, and the documented inactive-until-file-connected create behavior preserved. |
| `supplier-invoice-file-connections` | `Supplier Invoice File Connections` | 4 | `fortnox-api-tool supplier-invoice-file-connections` | Shipped | All documented operations are shipped with plan-first create and irreversible remove verification via follow-up GET. |
| `supplier-invoice-payments` | `Supplier Invoice Payments` | 6 | `fortnox-api-tool supplier-invoice-payments` | Shipped | All documented supplier-invoice-payment operations are shipped with plan-first writes and read-back verification. |
| `supplier-invoices` | `Supplier Invoices` | 9 | `fortnox-api-tool supplier-invoices` | Shipped | `list`, `get`, `create`, `update`, `approvalbookkeep`, `approvalpayment`, `bookkeep`, `cancel`, and `credit` are fully shipped and plan-first. |
| `suppliers` | `Suppliers` | 4 | `fortnox-api-tool suppliers` | Shipped | `list`, `get`, `create`, and `update` are wired locally with plan-first writes, explicit rendered list filters, and read-back verification. |
| `tax-reductions` | `Tax Reductions` | 5 | `fortnox-api-tool tax-reductions` | Shipped | All documented operations are shipped with plan-first writes and read-back verification. |
| `tenant` | `Tenant` | 1 | `fortnox-api-tool tenant` | Shipped | Read-only `get` is shipped. |
| `terms-of-deliveries` | `Terms Of Deliveries` | 4 | `fortnox-api-tool terms-of-deliveries` | Shipped | `list`, `get`, `create`, and `update` are fully shipped with plan-first writes and read-back verification. |
| `terms-of-payments` | `Terms Of Payments` | 5 | `fortnox-api-tool terms-of-payments` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and read-back/absence verification. |
| `units` | `Units` | 5 | `fortnox-api-tool units` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |
| `users` | `Users` | 1 | `fortnox-api-tool users` | Shipped | Read-only `fetch-user-information-for-a-single-published-integration-and-tenant` is shipped. |
| `vacation-debt-basis` | `Vacation Debt Basis` | 1 | `fortnox-api-tool vacation-debt-basis` | Shipped | Read-only `get` is shipped. |
| `voucher-file-connections` | `Voucher File Connections` | 4 | `fortnox-api-tool voucher-file-connections` | Shipped | All documented operations are shipped with plan-first create and irreversible remove verification via follow-up GET. |
| `voucher-series` | `Voucher Series` | 4 | `fortnox-api-tool voucher-series` | Shipped | `list`, `get`, `create`, and `update` are fully shipped with plan-first writes and verification. |
| `vouchers` | `Vouchers` | 5 | `fortnox-api-tool vouchers` | Shipped | All documented operations are shipped. |
| `way-of-deliveries` | `Way Of Deliveries` | 5 | `fortnox-api-tool way-of-deliveries` | Shipped | `list`, `get`, `create`, `update`, and `remove` are fully shipped with plan-first writes and verification. |

## REST per-operation ledger

Columns: ship status, group, family, HTTP method, REST path, official operation id, official title, planned CLI command, proof status, and notes.

### `absence-transactions` (6 operations)

- Official labels: `Absence Transactions`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/absencetransactions` | `AbsenceTransactionsController_doCreate` | Create a new absence transaction | `fortnox-api-tool absence-transactions create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by resolved response `id` plus read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/absencetransactions/{id}` | `AbsenceTransactionsController_doDelete` | Delete an absence transaction | `fortnox-api-tool absence-transactions delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/absencetransactions/{id}` | `AbsenceTransactionsController_doShow` | Retrieve a specific absence transaction | `fortnox-api-tool absence-transactions get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/absencetransactions/{id}/{Date}/{Code}` | `AbsenceTransactionsController_doListByIdDateCauseCode` | Retrieve absence transactions | `fortnox-api-tool absence-transactions get-by-employee-date-code` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. The rendered docs name the first path token `{id}`, but the CLI exposes it as `--employee-id` to match the documented meaning. |
| Shipped | `fortnox` | `GET` | `/3/absencetransactions` | `AbsenceTransactionsController_doIndex` | Lists all absence transactions | `fortnox-api-tool absence-transactions list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/absencetransactions/{id}` | `AbsenceTransactionsController_doUpdate` | Update a single absence transaction | `fortnox-api-tool absence-transactions update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `account-charts` (1 operations)

- Official labels: `Account Charts`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/accountcharts` | `AccountChartController_doIndex` | List all account charts | `fortnox-api-tool account-charts list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `accounts` (5 operations)

- Official labels: `Accounts`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/accounts` | `AccountController_doCreate` | Create an account | `fortnox-api-tool accounts create` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `DELETE` | `/3/accounts/{Number}` | `AccountController_doDelete` | Deletes an account | `fortnox-api-tool accounts delete` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/accounts/{Number}` | `AccountController_doShow` | Retrieve an account | `fortnox-api-tool accounts get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/accounts` | `AccountController_doIndex` | List all accounts | `fortnox-api-tool accounts list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/accounts/{Number}` | `AccountController_doUpdate` | Update an account | `fortnox-api-tool accounts update` | Local unit-tested / live-unverified |  |

### `archive` (5 operations)

- Official labels: `Archive`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `DELETE` | `/3/archive/{id}` | `ArchiveController_doDelete` | Delete a single file | `fortnox-api-tool archive delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, supports the documented optional `path` query, and verifies by follow-up absence. |
| Shipped | `fortnox` | `GET` | `/3/archive/{id}` | `ArchiveController_doShow` | Retrieve a single file | `fortnox-api-tool archive get-file` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/archive` | `ArchiveController_doIndex` | Retrieve folder or file | `fortnox-api-tool archive get-root` | Local unit-tested / live-unverified | Current shipped read supports the documented `path` and `fileid` query wiring only. |
| Shipped | `fortnox` | `DELETE` | `/3/archive` | `ArchiveController_doDeleteRoot` | Remove files | `fortnox-api-tool archive remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, requires explicit `--path` for safe targeting, and verifies by follow-up absence. |
| Shipped | `fortnox` | `POST` | `/3/archive` | `ArchiveController_doCreate` | Upload a file to a specific subdirectory | `fortnox-api-tool archive upload-a-file-to-a-specific-subdirectory` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, requires explicit `--path` or `--folder-id`, uploads multipart `file`, and verifies by read-back GET on the returned `Id`. |

### `article-file-connections` (4 operations)

- Official labels: `Article File Connections`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/articlefileconnections` | `ArticleFileConnectionController_doCreate` | Create an article file connection | `fortnox-api-tool article-file-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies presence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/articlefileconnections/{FileId}` | `ArticleFileConnectionController_doShow` | Retrieve a single article file connection | `fortnox-api-tool article-file-connections get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/articlefileconnections` | `ArticleFileConnectionController_doIndex` | Retrieve a list of article file connections | `fortnox-api-tool article-file-connections list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/articlefileconnections/{FileId}` | `ArticleFileConnectionController_doDelete` | Remove an article file connection | `fortnox-api-tool article-file-connections remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |

### `article-url-connections` (5 operations)

- Official labels: `Article Url Connections`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/articleurlconnections` | `ItemUrlConnectionController_doCreate` | Create an article url connection | `fortnox-api-tool article-url-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by follow-up GET using the returned `Id`. |
| Shipped | `fortnox` | `DELETE` | `/3/articleurlconnections/{id}` | `ItemUrlConnectionController_doDelete` | Remove an article url connection | `fortnox-api-tool article-url-connections delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/articleurlconnections/{id}` | `ItemUrlConnectionController_doShow` | Retrieve a single article url connection | `fortnox-api-tool article-url-connections get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/articleurlconnections` | `ItemUrlConnectionController_doIndex` | Retrieve a list of article url connections | `fortnox-api-tool article-url-connections list` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only and keeps the documented optional articlenumber query filter explicit. |
| Shipped | `fortnox` | `PUT` | `/3/articleurlconnections/{id}` | `ItemUrlConnectionController_doUpdate` | Update an article url connection | `fortnox-api-tool article-url-connections update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by follow-up GET. |

### `articles` (6 operations)

- Official labels: `Articles`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/articles` | `ArticleController_doCreate` | Create an article | `fortnox-api-tool articles create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/articles/{ArticleNumber}` | `ArticleController_doDelete` | Delete an article | `fortnox-api-tool articles delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/articles/{ArticleNumber}` | `ArticleController_doShow` | Retrieve an article | `fortnox-api-tool articles get` | Local unit-tested / live-unverified | Current shipped read matches the rendered docs: path selector only, with no extra query params shown there. |
| Shipped | `fortnox` | `GET` | `/3/articles` | `ArticleController_doIndex` | Retrieve a list of articles | `fortnox-api-tool articles list` | Local unit-tested / live-unverified | Current shipped read keeps the rendered `filter`, `sortby`, `articlenumber`, `description`, `ean`, `suppliernumber`, `manufacturer`, `manufacturerarticlenumber`, `webshop`, and `lastmodified` query params explicit. |
| Shipped | `time-reporting` | `GET` | `/api/time/articles-v1` | `list_8` | Get full article registrations that match filter | `fortnox-api-tool articles list-time-article-registrations` | Local unit-tested / live-unverified | Read-only. Current shipped read keeps the documented time-reporting GET separate from the Fortnox article CRUD paths. |
| Shipped | `fortnox` | `PUT` | `/3/articles/{ArticleNumber}` | `ArticleController_doUpdate` | Update an article | `fortnox-api-tool articles update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `asset-file-connections` (3 operations)

- Official labels: `fortnox_AssetFileConnection`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/assetfileconnections` | `AssetFileConnectionController_doCreate` | Create an asset file connection | `fortnox-api-tool asset-file-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies presence by follow-up `list` scan on `FileId`. |
| Shipped | `fortnox` | `GET` | `/3/assetfileconnections` | `AssetFileConnectionController_doIndex` | Retrieve a list of asset file connections | `fortnox-api-tool asset-file-connections list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/assetfileconnections/{FileId}` | `AssetFileConnectionController_doDelete` | Remove an asset file connection | `fortnox-api-tool asset-file-connections remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up `list` scan on `FileId`. |

### `asset-types` (5 operations)

- Official labels: `Asset Types`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/assets/types` | `AssetsController_doTypesPost` | Create an asset type | `fortnox-api-tool asset-types create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by resolved `Id` or fallback `Number` plus read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/assets/types/{id}` | `AssetsController_doTypesDeleteWithId` | Delete an asset type | `fortnox-api-tool asset-types delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/assets/types/{id}` | `AssetsController_doTypesGetWithId` | Retrieve an asset type | `fortnox-api-tool asset-types get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/assets/types` | `AssetsController_doTypesGet` | Retrieve a list of asset types | `fortnox-api-tool asset-types list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/assets/types/{id}` | `AssetsController_doTypesPutWithId` | Update an asset type | `fortnox-api-tool asset-types update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `Type.Id` when present, and verifies by read-back GET. |

### `assets` (12 operations)

- Official labels: `Assets`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/assets/depreciations/{ToDate}` | `AssetsController_doDepreciations` | Assets depreciation list | `fortnox-api-tool assets assets-depreciation-list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/assets/changeob/{Id}` | `AssetsController_doChangeob` | Change manual OB value of an Asset | `fortnox-api-tool assets change-manual-ob-value-of-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by follow-up asset read-back change detection. |
| Shipped | `fortnox` | `POST` | `/3/assets` | `AssetsController_doCreate` | Create an Asset | `fortnox-api-tool assets create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by resolved `Id` or fallback `Number` plus read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/assets/{Id}` | `AssetsController_doDelete` | Delete or Void an Asset | `fortnox-api-tool assets delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/assets/{Id}` | `AssetsController_doShow` | Retrieve a single asset | `fortnox-api-tool assets get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/assets` | `AssetsController_doIndex` | Retrieve a list of assets | `fortnox-api-tool assets list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `POST` | `/3/assets/depreciate` | `AssetsController_doDepreciate` | Perform a Depreciation of an Asset | `fortnox-api-tool assets perform-a-depreciation-of-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by the documented `AssetsDepreciation` response rows. |
| Shipped | `fortnox` | `PUT` | `/3/assets/scrap/{Id}` | `AssetsController_doScrap` | Scrap an Asset | `fortnox-api-tool assets scrap-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies by follow-up asset read-back change detection. |
| Shipped | `fortnox` | `PUT` | `/3/assets/sell/{Id}` | `AssetsController_doSell` | Sell an Asset | `fortnox-api-tool assets sell-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies by follow-up asset read-back change detection. |
| Shipped | `fortnox` | `PUT` | `/3/assets/{Id}` | `AssetsController_doUpdate` | Update an Asset | `fortnox-api-tool assets update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `Asset.Id` when present, and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/assets/writedown/{Id}` | `AssetsController_doWritedown` | Write down an Asset | `fortnox-api-tool assets write-down-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by follow-up asset read-back change detection. |
| Shipped | `fortnox` | `PUT` | `/3/assets/writeup/{Id}` | `AssetsController_doWriteup` | Write up an Asset | `fortnox-api-tool assets write-up-an-asset` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by follow-up asset read-back change detection. |

### `attachment` (6 operations)

- Official labels: `Attachment`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fileattachments` | `POST` | `/api/fileattachments/attachments-v1` | `attach` | Attach files to one or more entities | `fortnox-api-tool attachment attach-files-to-one-or-more-entities` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies each entity group by follow-up GET on the documented attachment list endpoint. |
| Shipped | `fileattachments` | `DELETE` | `/api/fileattachments/attachments-v1/{attachmentId}` | `detach` | Detach file | `fortnox-api-tool attachment detach-file` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies the documented `204` response only because the rendered docs do not expose a documented GET-by-attachment-id follow-up. |
| Shipped | `fileattachments` | `GET` | `/api/fileattachments/attachments-v1` | `getAttachments` | Get attached files on an entity | `fortnox-api-tool attachment get` | Local unit-tested / live-unverified | Read-only. Uses explicit repeated `--entity-id` plus documented `--entity-type` query wiring. |
| Shipped | `fileattachments` | `GET` | `/api/fileattachments/attachments-v1/numberofattachments` | `getNumberOfAttachmentsForEntity` | List number of attachments | `fortnox-api-tool attachment list` | Local unit-tested / live-unverified | Read-only. Uses explicit repeated `--entity-id` plus documented `--entity-type` query wiring for the count endpoint. |
| Shipped | `fileattachments` | `PUT` | `/api/fileattachments/attachments-v1/{attachmentId}` | `updateAttachment` | Update attachment | `fortnox-api-tool attachment update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces payload `id` match, and verifies by follow-up GET on the documented attachment list endpoint. |
| Shipped | `fileattachments` | `POST` | `/api/fileattachments/attachments-v1/validateincludedonsend` | `validateIncludedOnSend` | Validates a list of attachments that will be included on send | `fortnox-api-tool attachment validates-a-list-of-attachments-that-will-be-included-on-send` | Local unit-tested / live-unverified | Read-only validation POST. Sends the documented top-level attachment array and does not require write flags. |

### `attendance-transactions` (6 operations)

- Official labels: `Attendance Transactions`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/attendancetransactions` | `AttendanceTransactionsController_doCreate` | Create a new attendance transaction | `fortnox-api-tool attendance-transactions create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by resolved response `id` plus read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/attendancetransactions/{id}` | `AttendanceTransactionsController_doDelete` | Delete an attendance transaction | `fortnox-api-tool attendance-transactions delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/attendancetransactions/{id}` | `AttendanceTransactionsController_doShow` | Retrieve a specific attendance transaction | `fortnox-api-tool attendance-transactions get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/attendancetransactions/{id}/{Date}/{Code}` | `AttendanceTransactionsController_doListByIdDateCauseCode` | Retrieve attendance transactions | `fortnox-api-tool attendance-transactions get-by-employee-date-code` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. The rendered docs name the first path token `{id}`, but the CLI exposes it as `--employee-id` to match the documented meaning. |
| Shipped | `fortnox` | `GET` | `/3/attendancetransactions` | `AttendanceTransactionsController_doIndex` | Lists all attendance transactions | `fortnox-api-tool attendance-transactions list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/attendancetransactions/{id}` | `AttendanceTransactionsController_doUpdate` | Update a single attendance transaction | `fortnox-api-tool attendance-transactions update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `company-information` (1 operations)

- Official labels: `Company Information`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/companyinformation` | `CompanyInformationController_doIndex` | Retrieve the Company Information | `fortnox-api-tool company-information get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `company-settings` (1 operations)

- Official labels: `Company Settings`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/settings/company` | `CompanySettingsController_doIndex` | Retrieve the company settings | `fortnox-api-tool company-settings get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `contract-accruals` (5 operations)

- Official labels: `Contract Accruals`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/contractaccruals` | `ContractAccrualController_doCreate` | Create a contract accrual | `fortnox-api-tool contract-accruals create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/contractaccruals/{DocumentNumber}` | `ContractAccrualController_doShow` | Retrieve a single contract accrual | `fortnox-api-tool contract-accruals get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/contractaccruals` | `ContractAccrualController_doIndex` | Retrieve a list of contract accruals | `fortnox-api-tool contract-accruals list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/contractaccruals/{DocumentNumber}` | `ContractAccrualController_doDelete` | Remove a contract accrual | `fortnox-api-tool contract-accruals remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/contractaccruals/{DocumentNumber}` | `ContractAccrualController_doUpdate` | Update a contract accrual | `fortnox-api-tool contract-accruals update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `ContractAccrual.DocumentNumber` when present, and verifies by read-back GET. |

### `contract-templates` (4 operations)

- Official labels: `Contract Templates`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/contracttemplates` | `ContractTemplateController_doCreate` | Create a contract template | `fortnox-api-tool contract-templates create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/contracttemplates/{TemplateNumber}` | `ContractTemplateController_doShow` | Retrieve a single contract template | `fortnox-api-tool contract-templates get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/contracttemplates` | `ContractTemplateController_doIndex` | Retrieve a list of contract templates | `fortnox-api-tool contract-templates list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/contracttemplates/{TemplateNumber}` | `ContractTemplateController_doUpdate` | Update a contract template | `fortnox-api-tool contract-templates update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `ContractTemplate.TemplateNumber` when present, and verifies by read-back GET. |

### `contracts` (7 operations)

- Official labels: `Contracts`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/contracts` | `ContractController_doCreate` | Create a contract | `fortnox-api-tool contracts create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/contracts/{DocumentNumber}/createinvoice` | `ContractController_doUpdateAndCreateInvoice` | Create invoice from contract | `fortnox-api-tool contracts create-invoice` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes`, accepts optional wrapped `Contract` JSON plus optional `--invoice-date`, and verifies by before/after contract state. |
| Shipped | `fortnox` | `GET` | `/3/contracts/{DocumentNumber}` | `ContractController_doShow` | Retrieve a single contract | `fortnox-api-tool contracts get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/contracts/{DocumentNumber}/increaseinvoicecount` | `ContractController_doUpdateAndIncreaseInvoiceCount` | Increases the invoice count without creating an invoice | `fortnox-api-tool contracts increase-invoice-count` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes`, accepts an optional wrapped `Contract` JSON body, and verifies `InvoicesRemaining` increases after read-back. |
| Shipped | `fortnox` | `GET` | `/3/contracts` | `ContractController_doIndex` | Retrieve a list of contracts | `fortnox-api-tool contracts list` | Local unit-tested / live-unverified | Current shipped read supports the documented `periodstart`, `periodend`, `filter`, `documentnumber`, `customernumber`, `templatenumber`, `invoicesremaining`, and `lastmodified` query parameters. |
| Shipped | `fortnox` | `PUT` | `/3/contracts/{DocumentNumber}/finish` | `ContractController_doUpdateAndFinish` | Set a contract as finished | `fortnox-api-tool contracts finish` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes`, accepts an optional wrapped `Contract` JSON body, and verifies `Active == false` after read-back. |
| Shipped | `fortnox` | `PUT` | `/3/contracts/{DocumentNumber}` | `ContractController_doUpdate` | Update a contract | `fortnox-api-tool contracts update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `Contract.DocumentNumber` when present, and verifies by read-back GET. |

### `cost-centers` (5 operations)

- Official labels: `Cost Centers`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/costcenters` | `CostCenterController_doCreate` | Create a cost center | `fortnox-api-tool cost-centers create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET using the resolved `Code`. |
| Shipped | `fortnox` | `GET` | `/3/costcenters/{Code}` | `CostCenterController_doShow` | Retrieve a single cost center | `fortnox-api-tool cost-centers get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/costcenters` | `CostCenterController_doIndex` | Retrieve a list of cost centers | `fortnox-api-tool cost-centers list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/costcenters/{Code}` | `CostCenterController_doDelete` | Remove a cost center | `fortnox-api-tool cost-centers remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/costcenters/{Code}` | `CostCenterController_doUpdate` | Update a cost center | `fortnox-api-tool cost-centers update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `currencies` (5 operations)

- Official labels: `Currencies`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/currencies` | `CurrencyController_doCreate` | Create a currency | `fortnox-api-tool currencies create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET using the resolved `Code`. |
| Shipped | `fortnox` | `GET` | `/3/currencies/{Code}` | `CurrencyController_doShow` | Retrieve a single currency | `fortnox-api-tool currencies get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/currencies` | `CurrencyController_doIndex` | Retrieve a list of currencies | `fortnox-api-tool currencies list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/currencies/{Code}` | `CurrencyController_doDelete` | Remove a currency | `fortnox-api-tool currencies remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/currencies/{Code}` | `CurrencyController_doUpdate` | Update a currency | `fortnox-api-tool currencies update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `custom-document-types` (3 operations)

- Official labels: `Custom Document Type`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/documentdeliveries/custom/documenttypes-v1` | `create_8` | Create custom document type | `fortnox-api-tool custom-document-types create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, accepts the documented numeric JSON response, and verifies by read-back GET on `referenceType`. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/documentdeliveries/custom/documenttypes-v1/{type}` | `get_11` | Get custom document type | `fortnox-api-tool custom-document-types get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/documentdeliveries/custom/documenttypes-v1` | `getAll_6` | List custom document types | `fortnox-api-tool custom-document-types list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `custom-inbound-documents` (4 operations)

- Official labels: `Custom Inbound Document`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `GET` | `/api/warehouse/documentdeliveries/custom/inbound-v1/{type}/{id}` | `get_12` | Get custom inbound document | `fortnox-api-tool custom-inbound-documents get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/inbound-v1/{type}/{id}/release` | `release_4` | Release custom inbound document | `fortnox-api-tool custom-inbound-documents release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, re-checks the payload hash, and verifies by read-back `released=true`. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/inbound-v1/{type}/{id}` | `save` | Save custom inbound document | `fortnox-api-tool custom-inbound-documents save` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `referenceType` and `id` selector matches when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/inbound-v1/{type}/{id}/void` | `voidDocument_2` | Void custom inbound document | `fortnox-api-tool custom-inbound-documents void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies by read-back `voided=true`. |

### `custom-outbound-documents` (4 operations)

- Official labels: `Custom Outbound Document`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `GET` | `/api/warehouse/documentdeliveries/custom/outbound-v1/{type}/{id}` | `get_13` | Get custom outbound document | `fortnox-api-tool custom-outbound-documents get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/outbound-v1/{type}/{id}/release` | `release_5` | Release custom outbound document | `fortnox-api-tool custom-outbound-documents release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, re-checks the payload hash, and verifies by read-back `released=true`. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/outbound-v1/{type}/{id}` | `save_1` | Save a custom outbound document | `fortnox-api-tool custom-outbound-documents save` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `referenceType` and `id` selector matches when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/documentdeliveries/custom/outbound-v1/{type}/{id}/void` | `voidDocument_3` | Void custom outbound document | `fortnox-api-tool custom-outbound-documents void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies by read-back `voided=true`. |

### `customer-references` (5 operations)

- Official labels: `Customer References`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/customerreferences` | `CustomerReferenceController_doCreate` | Create a customer reference row | `fortnox-api-tool customer-references create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, resolves `CustomerReferenceRowId`, and verifies by follow-up GET. |
| Shipped | `fortnox` | `DELETE` | `/3/customerreferences/{CustomerReferenceRowId}` | `CustomerReferenceController_doDelete` | Delete a customer reference row | `fortnox-api-tool customer-references delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/customerreferences/{CustomerReferenceRowId}` | `CustomerReferenceController_doShow` | Retrieve a customer reference row | `fortnox-api-tool customer-references get` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/customerreferences` | `CustomerReferenceController_doIndex` | Retrieve a list of customers reference rows | `fortnox-api-tool customer-references list` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `PUT` | `/3/customerreferences/{CustomerReferenceRowId}` | `CustomerReferenceController_doUpdate` | Update a customer reference row | `fortnox-api-tool customer-references update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, enforces `CustomerReference.CustomerReferenceRowId` when present, and verifies by follow-up GET. |

### `customers` (5 operations)

- Official labels: `Customers`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/customers` | `CustomerController_doCreate` | Create a customer | `fortnox-api-tool customers create` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `DELETE` | `/3/customers/{CustomerNumber}` | `CustomerController_doDelete` | Delete a customer | `fortnox-api-tool customers delete` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/customers/{CustomerNumber}` | `CustomerController_doShow` | Retrieve a customer | `fortnox-api-tool customers get` | Local unit-tested / live-unverified | Current shipped read matches the rendered docs: path selector only, with no extra query params shown there. |
| Shipped | `fortnox` | `GET` | `/3/customers` | `CustomerController_doIndex` | Retrieve a list of customers | `fortnox-api-tool customers list` | Local unit-tested / live-unverified | Current shipped read keeps the rendered `filter`, `sortby`, `customernumber`, `name`, `zipcode`, `city`, `email`, `phone`, `organisationnumber`, `gln`, `glndelivery`, and `lastmodified` query params explicit. |
| Shipped | `fortnox` | `PUT` | `/3/customers/{CustomerNumber}` | `CustomerController_doUpdate` | Update a customer | `fortnox-api-tool customers update` | Local unit-tested / live-unverified |  |

### `email-senders` (3 operations)

- Official labels: `Email Senders`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/emailsenders/trusted` | `EmailSenderController_doTrustedPostDefault` | Add a new email address as trusted | `fortnox-api-tool email-senders add-a-new-email-address-as-trusted` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, uses the documented `TrustedSender` wrapper, and verifies by follow-up trusted-sender list lookup. |
| Shipped | `fortnox` | `DELETE` | `/3/emailsenders/trusted/{Id}` | `EmailSenderController_doTrustedDeleteWithId` | Delete an email address from the trusted senders list | `fortnox-api-tool email-senders delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies absence by follow-up trusted-sender list lookup. |
| Shipped | `fortnox` | `GET` | `/3/emailsenders` | `EmailSenderController_doIndex` | Retrieve a list of all trusted and rejected senders | `fortnox-api-tool email-senders list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `employees` (4 operations)

- Official labels: `Employees`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/employees` | `EmployeeController_doCreate` | Create a new employee | `fortnox-api-tool employees create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, resolves `EmployeeId` from the response or payload, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/employees/{EmployeeId}` | `EmployeeController_doShow` | Retrieve a specific employee | `fortnox-api-tool employees get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/employees` | `EmployeeController_doIndex` | Retrieve a list of employees | `fortnox-api-tool employees list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/employees/{EmployeeId}` | `EmployeeController_doUpdate` | Update employee | `fortnox-api-tool employees update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `Employee.EmployeeId` when present, and verifies by read-back GET. |

### `eu-vat-limit-regulation` (1 operations)

- Official labels: `EU Vat Limit Regulation`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/euvatlimitregulation` | `EUVatLimitRegulationController_doIndex` | Retrieve details about eu vat limit | `fortnox-api-tool eu-vat-limit-regulation get` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only and keeps the documented optional `year` query filter explicit. |

### `expenses` (3 operations)

- Official labels: `Expenses`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/expenses` | `ExpensesController_doCreate` | Create an expense | `fortnox-api-tool expenses create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, resolves `ExpenseCode`, and verifies by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/expenses/{ExpenseCode}` | `ExpensesController_doShow` | Retrieve an expense | `fortnox-api-tool expenses get` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/expenses` | `ExpensesController_doIndex` | Retrieve expenses | `fortnox-api-tool expenses list` | Local unit-tested / live-unverified |  |

### `financial-years` (3 operations)

- Official labels: `Financial Years`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/financialyears` | `FinancialYearController_doCreate` | Create a financial year | `fortnox-api-tool financial-years create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/financialyears/{Id}` | `FinancialYearController_doShow` | Retrieve financial year by id | `fortnox-api-tool financial-years get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/financialyears` | `FinancialYearController_doIndex` | Retrieve a list of financial years | `fortnox-api-tool financial-years list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `fortnox-finans` (7 operations)

- Official labels: `Fortnox Finans`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/noxfinansinvoices/{InvoiceNumber}/pause` | `NoxInvoiceController_doUpdateAndPause` | Action Pause | `fortnox-api-tool fortnox-finans action-pause` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, uses the documented `NoxFinansInvoice` wrapper, and verifies by follow-up GET because the rendered docs do not pin one stable pause-state field. |
| Shipped | `fortnox` | `PUT` | `/3/noxfinansinvoices/{InvoiceNumber}/report-payment` | `NoxInvoiceController_doUpdateAndRepostPayment` | Action Report Payment | `fortnox-api-tool fortnox-finans action-report-payment` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, uses the documented `NoxFinansInvoice` wrapper, and verifies by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/noxfinansinvoices/{InvoiceNumber}/stop` | `NoxInvoiceController_doUpdateAndStop` | Action Stop | `fortnox-api-tool fortnox-finans action-stop` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, sends no request body unless a reviewed JSON payload was supplied, and verifies by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/noxfinansinvoices/{InvoiceNumber}/take-fees` | `NoxInvoiceController_doUpdateAndTakeFees` | Action Take Fees | `fortnox-api-tool fortnox-finans action-take-fees` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, sends no request body unless a reviewed JSON payload was supplied, and verifies by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/noxfinansinvoices/{InvoiceNumber}/unpause` | `NoxInvoiceController_doUpdateAndUnpause` | Action Unpause | `fortnox-api-tool fortnox-finans action-unpause` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, sends no request body unless a reviewed JSON payload was supplied, and verifies by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/noxfinansinvoices/{InvoiceNumber}` | `NoxInvoiceController_doShow` | Retrieve a single invoice payment | `fortnox-api-tool fortnox-finans get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `POST` | `/3/noxfinansinvoices` | `NoxInvoiceController_doCreate` | Send an invoice with Fortnox Finans | `fortnox-api-tool fortnox-finans send-an-invoice-with-fortnox-finans` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, uses the documented `NoxFinansInvoice` wrapper, and verifies by follow-up GET. The official docs note this can start live finance processing and may stay `UNKNOWN` or `NOT_AUTHORIZED` for some time. |

### `inbox` (4 operations)

- Official labels: `Inbox`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/inbox/{Id}` | `InboxController_doShow` | Retrieve a single file | `fortnox-api-tool inbox get-file` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/inbox` | `InboxController_doIndex` | Retrieve the root folder containing files and folders | `fortnox-api-tool inbox get-root` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/inbox/{Id}` | `InboxController_doDelete` | Remove a file or folder | `fortnox-api-tool inbox remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies by follow-up absence. |
| Shipped | `fortnox` | `POST` | `/3/inbox` | `InboxController_doCreate` | Upload a file | `fortnox-api-tool inbox upload-a-file` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, uploads multipart `file`, supports the documented `folderId` and `path` query selectors, and verifies by read-back GET on the returned `Id`. |

### `incoming-goods` (8 operations)

- Official labels: `Incoming Goods`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `PUT` | `/api/warehouse/incominggoods-v1/{id}/completed` | `completed` | Complete Incoming Goods document | `fortnox-api-tool incoming-goods complete-incoming-goods-document` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, sends the documented raw JSON string bookkeeping date, and verifies `completed == true` by follow-up GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/incominggoods-v1` | `create_9` | Create Incoming Goods document | `fortnox-api-tool incoming-goods create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, and verifies by resolved response `id` plus read-back GET. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/incominggoods-v1/{id}` | `get_15` | Get Incoming Goods document | `fortnox-api-tool incoming-goods get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/incominggoods-v1` | `getAll_7` | List Incoming Goods Documents | `fortnox-api-tool incoming-goods list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PATCH` | `/api/warehouse/incominggoods-v1/{id}` | `patch` | Partial update Incoming Goods document | `fortnox-api-tool incoming-goods partial-update-incoming-goods-document` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw partial payload shape, and verifies by read-back GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/incominggoods-v1/{id}/release` | `release_6` | Release Incoming Goods document | `fortnox-api-tool incoming-goods release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies `released == true` by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/incominggoods-v1/{id}` | `save_2` | Update Incoming Goods document | `fortnox-api-tool incoming-goods update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, enforces `id` when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/incominggoods-v1/{id}/void` | `voidDocument_4` | Void Incoming Goods document | `fortnox-api-tool incoming-goods void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies `voided == true` by follow-up GET. |

### `integration-ratings` (1 operations)

- Official labels: `Integration Ratings`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `integration-developer` | `GET` | `/api/integration-developer/ratings-v1` | `listRatings` | List rating and reviews for integrations that you own | `fortnox-api-tool integration-ratings list` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only and keeps the documented array response shape intact. |

### `integration-sales` (3 operations)

- Official labels: `Integration Sales`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `Developer` | `GET` | `/api/integration-partner/apps/sales-v1/{appId}` | `getAppSalesForSingleApp` | Resolves sales information and active users of an integration Deprecated | `fortnox-api-tool integration-sales get-by-app-id` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only. The rendered docs mark this endpoint deprecated. |
| Shipped | `Developer` | `GET` | `/api/integration-partner/apps/sales-v1/{appId}/{tenantId}` | `getAppSalesForSingleAppAndTenant` | Resolves sales information and active users of an integration Deprecated | `fortnox-api-tool integration-sales get-by-app-id-and-tenant` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only. The rendered docs mark this endpoint deprecated. |
| Shipped | `Developer` | `GET` | `/api/integration-developer/sales-v1/{integrationId}` | `getSalesForSingleIntegration` | Resolves sales information of an integration | `fortnox-api-tool integration-sales resolves-sales-information-of-an-integration` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only. |

### `invoice-accruals` (5 operations)

- Official labels: `Invoice Accruals`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/invoiceaccruals` | `InvoiceAccrualController_doCreate` | Create an invoice accrual | `fortnox-api-tool invoice-accruals create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/invoiceaccruals/{InvoiceNumber}` | `InvoiceAccrualController_doShow` | Retrieve a single invoice accrual | `fortnox-api-tool invoice-accruals get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/invoiceaccruals` | `InvoiceAccrualController_doIndex` | Retrieve a list of invoice accruals | `fortnox-api-tool invoice-accruals list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/invoiceaccruals/{InvoiceNumber}` | `InvoiceAccrualController_doDelete` | Remove an invoice accrual | `fortnox-api-tool invoice-accruals remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes --ack-irreversible` and verifies by follow-up absence check. |
| Shipped | `fortnox` | `PUT` | `/3/invoiceaccruals/{InvoiceNumber}` | `InvoiceAccrualController_doUpdate` | Update an invoice accrual | `fortnox-api-tool invoice-accruals update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `invoice-payments` (6 operations)

- Official labels: `Invoice Payments`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/invoicepayments/{Number}/bookkeep` | `InvoicePaymentController_doUpdateAndBookkeep` | Bookkeep an invoice payment | `fortnox-api-tool invoice-payments bookkeep` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Booked == true` after write. |
| Shipped | `fortnox` | `POST` | `/3/invoicepayments` | `InvoicePaymentController_doCreate` | Create an invoice payment | `fortnox-api-tool invoice-payments create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/invoicepayments/{Number}` | `InvoicePaymentController_doShow` | Retrieve a single invoice payment | `fortnox-api-tool invoice-payments get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/invoicepayments` | `InvoicePaymentController_doIndex` | Retrieve a list of invoice payments | `fortnox-api-tool invoice-payments list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/invoicepayments/{Number}` | `InvoicePaymentController_doDelete` | Remove an invoice payment | `fortnox-api-tool invoice-payments remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires reviewed `--plan-in --yes --ack-irreversible` and verifies by follow-up absence check. |
| Shipped | `fortnox` | `PUT` | `/3/invoicepayments/{Number}` | `InvoicePaymentController_doUpdate` | Update an invoice payment | `fortnox-api-tool invoice-payments update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `invoices` (15 operations)

- Official labels: `Invoices`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}/bookkeep` | `InvoiceController_doUpdateAndBookkeep` | Bookkeep an invoice | `fortnox-api-tool invoices bookkeep` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}/cancel` | `InvoiceController_doUpdateAndCancel` | Cancel an invoice | `fortnox-api-tool invoices cancel` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `POST` | `/3/invoices` | `InvoiceController_doCreate` | Create an invoice | `fortnox-api-tool invoices create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}/credit` | `InvoiceController_doUpdateAndCredit` | Credit an invoice | `fortnox-api-tool invoices credit` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}` | `InvoiceController_doShow` | Retrieve a single invoice | `fortnox-api-tool invoices get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/invoices` | `InvoiceController_doIndex` | Retrieve a list of invoices | `fortnox-api-tool invoices list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/preview` | `InvoiceController_doShowAndPreview` | Preview an invoice | `fortnox-api-tool invoices preview` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/print` | `InvoiceController_doShowAndPrint` | Print an invoice | `fortnox-api-tool invoices print` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/printreminder` | `InvoiceController_doShowAndPrintReminder` | Print an invoice as reminder | `fortnox-api-tool invoices print-reminder` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/einvoice` | `InvoiceController_doShowAndEinvoice` | Send an invoice as e-invoice | `fortnox-api-tool invoices send-an-invoice-as-e-invoice` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, calls the documented GET delivery action, and verifies `Sent == true` by follow-up GET. The official docs note extra invoice-data prerequisites such as delivery country in some cases. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/eprint` | `InvoiceController_doShowAndEprint` | Send an invoice as e-print | `fortnox-api-tool invoices send-an-invoice-as-e-print` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, calls the documented GET delivery action, and verifies `Sent == true` by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/invoices/{DocumentNumber}/email` | `InvoiceController_doShowAndEmail` | Send an invoice as email | `fortnox-api-tool invoices send-an-invoice-as-email` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, calls the documented GET delivery action, and verifies `Sent == true` by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}/warehouseready` | `InvoiceController_doUpdateAndWarehouseReady` | Set an invoice as done | `fortnox-api-tool invoices warehouseready` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}/externalprint` | `InvoiceController_doUpdateAndExternalPrint` | Set an invoice as sent | `fortnox-api-tool invoices externalprint` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/invoices/{DocumentNumber}` | `InvoiceController_doUpdate` | Update an invoice | `fortnox-api-tool invoices update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `labels` (4 operations)

- Official labels: `Labels`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/labels` | `DocumentTagController_doCreate` | Create a label | `fortnox-api-tool labels create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, resolves `Id`, and verifies by follow-up labels list scan. |
| Shipped | `fortnox` | `DELETE` | `/3/labels/{Id}` | `DocumentTagController_doDelete` | Delete a label | `fortnox-api-tool labels delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies absence by follow-up labels list scan. |
| Shipped | `fortnox` | `GET` | `/3/labels` | `DocumentTagController_doIndex` | Retrieve a list of labels | `fortnox-api-tool labels list` | Local unit-tested / live-unverified | The current rendered docs in this environment show only the list plus create, update, and delete operations for labels. |
| Shipped | `fortnox` | `PUT` | `/3/labels/{Id}` | `DocumentTagController_doUpdate` | Update a label | `fortnox-api-tool labels update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, enforces `Label.Id` when present, and verifies by follow-up labels list scan. |

### `locked-period` (1 operations)

- Official labels: `Locked Period`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/settings/lockedperiod` | `LockedPeriodSettingsController_doShow` | Retrieve the locked period | `fortnox-api-tool locked-period get` | Local unit-tested / live-unverified |  |

### `manual-documents` (1 operations)

- Official labels: `Manual Document`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `GET` | `/api/warehouse/deliveries-v1` | `getAll` | List manual documents | `fortnox-api-tool manual-documents list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `manual-inbound-documents` (6 operations)

- Official labels: `Manual Inbound Document`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/deliveries-v1/inbounddeliveries` | `create` | Create manual inbound document | `fortnox-api-tool manual-inbound-documents create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, uses the documented raw object payload, and verifies by read-back GET on the created `id`. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/deliveries-v1/inbounddeliveries/{id}` | `get` | Get manual inbound document | `fortnox-api-tool manual-inbound-documents get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/inbounddeliveries/{id}/release` | `release` | Release manual inbound document | `fortnox-api-tool manual-inbound-documents release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, re-checks the payload hash, and verifies by read-back `released=true`. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/inbounddeliveries/{id}` | `update` | Update manual inbound document | `fortnox-api-tool manual-inbound-documents update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `id` selector matches when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PATCH` | `/api/warehouse/deliveries-v1/inbounddeliveries/{id}` | `updateNote` | Update note on manual inbound document | `fortnox-api-tool manual-inbound-documents update-note` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `id` selector matches when present, and verifies by read-back note match. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/inbounddeliveries/{id}/void` | `voidDocument` | Void manual inbound document | `fortnox-api-tool manual-inbound-documents void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies by read-back `voided=true`. |

### `manual-outbound-documents` (6 operations)

- Official labels: `Manual Outbound Document`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/deliveries-v1/outbounddeliveries` | `create_1` | Create manual outbound document | `fortnox-api-tool manual-outbound-documents create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, uses the documented raw object payload, and verifies by read-back GET on the created `id`. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/deliveries-v1/outbounddeliveries/{id}` | `get_1` | Get manual outbound document | `fortnox-api-tool manual-outbound-documents get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/outbounddeliveries/{id}/release` | `release_1` | Release manual outbound document | `fortnox-api-tool manual-outbound-documents release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, re-checks the payload hash, and verifies by read-back `released=true`. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/outbounddeliveries/{id}` | `update_1` | Update manual outbound document | `fortnox-api-tool manual-outbound-documents update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `id` selector matches when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PATCH` | `/api/warehouse/deliveries-v1/outbounddeliveries/{id}` | `updateNote_1` | Update note on manual outbound document | `fortnox-api-tool manual-outbound-documents update-note` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `id` selector matches when present, and verifies by read-back note match. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/deliveries-v1/outbounddeliveries/{id}/void` | `voidDocument_1` | Void manual outbound document | `fortnox-api-tool manual-outbound-documents void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies by read-back `voided=true`. |

### `me` (1 operations)

- Official labels: `Me`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/me` | `MeController_doIndex` | Retrieve user information Use this endpoint to retrieve user information related to the used access token | `fortnox-api-tool auth check` | Local unit-tested / live-unverified | Used by the shipped live auth-check probe for token validation. |

### `modes-of-payments` (5 operations)

- Official labels: `Modes Of Payments`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/modesofpayments` | `ModeOfPaymentController_doCreate` | Create a mode of payment | `fortnox-api-tool modes-of-payments create` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/modesofpayments/{Code}` | `ModeOfPaymentController_doShow` | Retrieve a single mode of payment | `fortnox-api-tool modes-of-payments get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/modesofpayments` | `ModeOfPaymentController_doIndex` | Retrieve a list of modes of payments | `fortnox-api-tool modes-of-payments list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/modesofpayments/{Code}` | `ModeOfPaymentController_doDelete` | Remove a mode of payment | `fortnox-api-tool modes-of-payments remove` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `PUT` | `/3/modesofpayments/{Code}` | `ModeOfPaymentController_doUpdate` | Update a mode of payment | `fortnox-api-tool modes-of-payments update` | Local unit-tested / live-unverified |  |

### `offers` (11 operations)

- Official labels: `Offers`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/offers/{DocumentNumber}/cancel` | `OfferController_doUpdateAndCancel` | Cancels given offer | `fortnox-api-tool offers cancel` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `POST` | `/3/offers` | `OfferController_doCreate` | Create an offer | `fortnox-api-tool offers create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/offers/{DocumentNumber}/createinvoice` | `OfferController_doUpdateAndCreateInvoice` | Create invoice out of given offer | `fortnox-api-tool offers create-invoice` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/offers/{DocumentNumber}/createorder` | `OfferController_doUpdateAndCreateOrder` | Create order out of given offer | `fortnox-api-tool offers create-order` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/offers/{DocumentNumber}` | `OfferController_doShow` | Retrieve a single offer | `fortnox-api-tool offers get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/offers` | `OfferController_doIndex` | Retrieve a list of offers | `fortnox-api-tool offers list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/offers/{DocumentNumber}/preview` | `OfferController_doShowAndPreview` | Preview given offer | `fortnox-api-tool offers preview` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/offers/{DocumentNumber}/print` | `OfferController_doShowAndPrint` | Print given offer | `fortnox-api-tool offers print` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/offers/{DocumentNumber}/email` | `OfferController_doShowAndEmail` | Send given offer as email | `fortnox-api-tool offers send-given-offer-as-email` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, calls the documented GET delivery action, and verifies `Sent == true` by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/offers/{DocumentNumber}/externalprint` | `OfferController_doUpdateAndExternalPrint` | Set given offer as sent | `fortnox-api-tool offers externalprint` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/offers/{DocumentNumber}` | `OfferController_doUpdate` | Update an offer | `fortnox-api-tool offers update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `orders` (10 operations)

- Official labels: `Orders`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/orders/{DocumentNumber}/cancel` | `OrderController_doUpdateAndCancel` | Cancels given order | `fortnox-api-tool orders cancel` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `POST` | `/3/orders` | `OrderController_doCreate` | Create a new order | `fortnox-api-tool orders create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/orders/{DocumentNumber}/createinvoice` | `OrderController_doUpdateAndCreateOrder` | Create invoice out of given order | `fortnox-api-tool orders create-invoice` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/orders/{DocumentNumber}` | `OrderController_doShow` | Retrieve a single order | `fortnox-api-tool orders get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/orders` | `OrderController_doIndex` | Retrieve a list of orders | `fortnox-api-tool orders list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/orders/{DocumentNumber}/preview` | `OrderController_doShowAndPreview` | Preview given offer | `fortnox-api-tool orders preview` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/orders/{DocumentNumber}/print` | `OrderController_doShowAndPrint` | Print given order | `fortnox-api-tool orders print` | Local unit-tested / live-unverified | Read-only PDF output. The CLI returns PDF bytes as base64 by default or writes them to `--output-file` when requested. |
| Shipped | `fortnox` | `GET` | `/3/orders/{DocumentNumber}/email` | `OrderController_doShowAndEmail` | Send given order as email | `fortnox-api-tool orders send-given-order-as-email` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, calls the documented GET delivery action, and verifies `Sent == true` by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/orders/{DocumentNumber}/externalprint` | `OrderController_doUpdateAndExternalPrint` | Set given order as sent | `fortnox-api-tool orders externalprint` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/orders/{DocumentNumber}` | `OrderController_doUpdate` | Update an order | `fortnox-api-tool orders update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `predefined-accounts` (3 operations)

- Official labels: `Pre Defined Accounts`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/predefinedaccounts/{name}` | `PreDefinedAccountController_doShow` | Retrieve information for a specific account type | `fortnox-api-tool predefined-accounts get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/predefinedaccounts` | `PreDefinedAccountController_doIndex` | Retrieve a list of all predefined accounts | `fortnox-api-tool predefined-accounts list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/predefinedaccounts/{name}` | `PreDefinedAccountController_doUpdate` | Update a Predefined Account | `fortnox-api-tool predefined-accounts update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `predefined-voucher-series` (3 operations)

- Official labels: `Predefined Voucher Series`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/predefinedvoucherseries/{Name}` | `PreDefinedVoucherSeriesController_doShow` | Retrieve a specific predefined voucher series | `fortnox-api-tool predefined-voucher-series get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/predefinedvoucherseries` | `PreDefinedVoucherSeriesController_doIndex` | Retrieve a list of predefined voucher series | `fortnox-api-tool predefined-voucher-series list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/predefinedvoucherseries/{Name}` | `PreDefinedVoucherSeriesController_doUpdate` | Update a predefined voucher series | `fortnox-api-tool predefined-voucher-series update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |

### `price-lists` (4 operations)

- Official labels: `Price Lists`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/pricelists` | `PriceListController_doCreate` | Create a price list | `fortnox-api-tool price-lists create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/pricelists/{Code}` | `PriceListController_doShow` | Retrieve a single price list | `fortnox-api-tool price-lists get` | Local unit-tested / live-unverified | Current shipped read matches the rendered docs: path selector only, with no extra query params shown there. |
| Shipped | `fortnox` | `GET` | `/3/pricelists` | `PriceListController_doIndex` | Retrieve a list of price lists | `fortnox-api-tool price-lists list` | Local unit-tested / live-unverified | Current shipped read matches the rendered docs: no query parameters are shown on the rendered list operation. |
| Shipped | `fortnox` | `PUT` | `/3/pricelists/{Code}` | `PriceListController_doUpdate` | Update a price list | `fortnox-api-tool price-lists update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `prices` (8 operations)

- Official labels: `Prices`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/prices` | `PriceController_doCreate` | Create a price | `fortnox-api-tool prices create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET on the resolved composite price key. |
| Shipped | `fortnox` | `DELETE` | `/3/prices/{PriceList}/{ArticleNumber}/{FromQuantity}` | `PriceController_doDeleteWithId3` | Delete a single price | `fortnox-api-tool prices delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/prices/{PriceList}/{ArticleNumber}` | `PriceController_doShow` | Retrieve the first price for the specified article | `fortnox-api-tool prices get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/prices/{PriceList}/{ArticleNumber}/{FromQuantity}` | `PriceController_doShowWithId3` | Retrieve a price for a specified article | `fortnox-api-tool prices get-by-from-quantity` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/prices` | `PriceController_doIndex` | Retrieve a list of prices | `fortnox-api-tool prices list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/prices/sublist/{PriceList}/{ArticleNumber}` | `PriceController_doSublistWithTwoParams` | Retrieve a list of articles with all their prices in the specified price list | `fortnox-api-tool prices list-sublist` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/prices/{PriceList}/{ArticleNumber}` | `PriceController_doUpdate` | Update the first price in the specified article | `fortnox-api-tool prices update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/prices/{PriceList}/{ArticleNumber}/{FromQuantity}` | `PriceController_doUpdateWithId3` | Update a price | `fortnox-api-tool prices update-by-from-quantity` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `print-templates` (1 operations)

- Official labels: `Print Templates`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/printtemplates` | `PrintTemplateController_doIndex` | Retrieve a list of print templates | `fortnox-api-tool print-templates list` | Local unit-tested / live-unverified |  |

### `production-orders` (8 operations)

- Official labels: `Production Order`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/productionorders-v1` | `create_10` | Create a new production order | `fortnox-api-tool production-orders create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the official raw warehouse payload shape, and verifies by resolved response `id` plus follow-up GET. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/productionorders-v1/{id}` | `get_16` | Get Production Order document | `fortnox-api-tool production-orders get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/productionorders-v1/billofmaterials/{itemId}` | `getRequiredProductionParts` | Get the package items (Bill Of Materials, BOMs) for a production article | `fortnox-api-tool production-orders get-bill-of-materials` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/productionorders-v1` | `getAll_8` | List production orders | `fortnox-api-tool production-orders list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/productionorders-v1/release/{id}` | `release_7` | Release a production order document | `fortnox-api-tool production-orders release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/productionorders-v1/{id}` | `update_5` | Update a production order | `fortnox-api-tool production-orders update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the official raw warehouse payload shape, enforces `id` when present, and verifies by follow-up GET. |
| Shipped | `warehouse` | `PATCH` | `/api/warehouse/productionorders-v1/{id}` | `updateNote_2` | Update the note of a production order | `fortnox-api-tool production-orders update-note` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the documented PATCH note path, enforces `id` when present, and verifies by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/productionorders-v1/void/{id}` | `voidProductionOrder` | Void a production order | `fortnox-api-tool production-orders void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies by follow-up GET. |

### `projects` (5 operations)

- Official labels: `Projects`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/projects` | `ProjectsController_doCreate` | Create a project | `fortnox-api-tool projects create` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/projects/{ProjectNumber}` | `ProjectsController_doShow` | Retrieve a single project | `fortnox-api-tool projects get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/projects` | `ProjectsController_doIndex` | Retrieve a list of projects | `fortnox-api-tool projects list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/projects/{ProjectNumber}` | `ProjectsController_doDelete` | Remove a project | `fortnox-api-tool projects remove` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `PUT` | `/3/projects/{ProjectNumber}` | `ProjectsController_doUpdate` | Update a project | `fortnox-api-tool projects update` | Local unit-tested / live-unverified |  |

### `purchase-orders` (15 operations)

- Official labels: `Purchase Order`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/purchaseorders-v1` | `create_11` | Create Purchase Order | `fortnox-api-tool purchase-orders create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, and verifies by resolved response `id` plus read-back GET. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/purchaseorders-v1/{id}` | `get_17` | Get Purchase Order | `fortnox-api-tool purchase-orders get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/purchaseorders-v1/csv` | `getCsvReport` | Get CSV list of Purchase Orders | `fortnox-api-tool purchase-orders get-csv` | Local unit-tested / live-unverified | Current shipped read keeps the official CSV/text response instead of forcing JSON parsing. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/purchaseorders-v1/{id}/notes` | `getAttachedNotes` | Get notes | `fortnox-api-tool purchase-orders get-note` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/purchaseorders-v1` | `getAll_9` | List Purchase Orders | `fortnox-api-tool purchase-orders list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/purchaseorders-v1/{id}/matches` | `getMatchedDocuments_1` | List matched documents | `fortnox-api-tool purchase-orders list-matches` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/{id}/dropshipcomplete` | `setDropshipManuallyCompleted` | Manually complete dropship order | `fortnox-api-tool purchase-orders manually-complete-dropship-order` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies the manual-completion state by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/{id}/complete` | `setManuallyCompleted` | Manually complete Purchase Order | `fortnox-api-tool purchase-orders manually-complete-purchase-order` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies the manual-completion state by follow-up GET. |
| Shipped | `warehouse` | `PATCH` | `/api/warehouse/purchaseorders-v1/{id}/partial` | `updatePartial` | Partial update Purchase Order | `fortnox-api-tool purchase-orders partial-update-purchase-order` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw partial payload shape, and verifies by read-back GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/purchaseorders-v1/{id}/send` | `sendPurchaseOrder` | Send purchase order via email | `fortnox-api-tool purchase-orders send-purchase-order-via-email` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies `purchaseOrderState == SENT` by follow-up GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/purchaseorders-v1/sendpurchaseorders` | `sendPurchaseOrders` | Sends multiple purchase orders via email | `fortnox-api-tool purchase-orders sends-multiple-purchase-orders-via-email` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, uses repeated `--id` flags for the documented raw id array, and verifies `purchaseOrderState == SENT` for every target. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/{id}` | `update_6` | Update Purchase Order | `fortnox-api-tool purchase-orders update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, enforces `id` when present, and verifies by read-back GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/{id}/response` | `updateResponseState` | Update response state | `fortnox-api-tool purchase-orders update-response` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, keeps the raw `{ "responseState": ... }` payload, and verifies response-state read-back. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/response` | `batchUpdateResponseState` | Update response states | `fortnox-api-tool purchase-orders update-response-bulk` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in`, uses repeated `--id` flags for the documented `ids` query parameter, and verifies response-state read-back for every target. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/purchaseorders-v1/{id}/void` | `voidDocument_5` | Void Purchase Order | `fortnox-api-tool purchase-orders void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies the voided state by follow-up GET. |

### `registrations` (1 operations)

- Official labels: `Registrations`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `time-reporting` | `GET` | `/api/time/registrations-v2` | `list_2` | Get time/absence registrations that match filter | `fortnox-api-tool registrations get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only and uses the official `/api/time/registrations-v2` endpoint. |

### `salary-transactions` (5 operations)

- Official labels: `Salary Transactions`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/salarytransactions` | `SalaryTransactionsController_doCreate` | Create a new salary transaction for an employee | `fortnox-api-tool salary-transactions create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, resolves `SalaryRow` from the response or payload, and verifies by read-back GET. |
| Shipped | `fortnox` | `DELETE` | `/3/salarytransactions/{SalaryRow}` | `SalaryTransactionsController_doDelete` | Delete a single salary transaction | `fortnox-api-tool salary-transactions delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/salarytransactions/{SalaryRow}` | `SalaryTransactionsController_doShow` | Retrieve a single salary transaction | `fortnox-api-tool salary-transactions get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/salarytransactions` | `SalaryTransactionsController_doIndex` | List all salary transactions for all employees | `fortnox-api-tool salary-transactions list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/salarytransactions/{SalaryRow}` | `SalaryTransactionsController_doUpdate` | Update a salary transaction | `fortnox-api-tool salary-transactions update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `SalaryTransaction.SalaryRow` when present, and verifies by read-back GET. |

### `schedule-times` (3 operations)

- Official labels: `Schedule Times`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/scheduletimes/{EmployeeId}/{Date}` | `ScheduleTimeController_doShow` | Retrieve a specific schedule time | `fortnox-api-tool schedule-times get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/scheduletimes/{EmployeeId}/{Date}/resetday` | `ScheduleTimeController_doUpdateAndResetDay` | Reset schedule time | `fortnox-api-tool schedule-times reset-day` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, validates payload `ScheduleTime.EmployeeId` and `ScheduleTime.Date` when present, and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/scheduletimes/{EmployeeId}/{Date}` | `ScheduleTimeController_doUpdate` | Update a schedule time | `fortnox-api-tool schedule-times update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, validates payload `ScheduleTime.EmployeeId` and `ScheduleTime.Date` when present, and verifies by read-back GET. |

### `sie` (1 operations)

- Official labels: `Sie`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/sie/{Type}` | `SieController_doShow` | Retrieve a SIE file | `fortnox-api-tool sie get` | Local unit-tested / live-unverified | Read-only. Current shipped read keeps the documented streamed/octet-stream response as plain text output and keeps `selection`, `financialYear`, `exportall`, `fromdate`, and `todate` explicit. |

### `stock-points` (8 operations)

- Official labels: `Stock Point`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/stockpoints-v1/{id}` | `appendStockLocations` | Append stock locations | `fortnox-api-tool stock-points append-stock-locations` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the documented raw top-level `StockLocation[]` payload, and verifies appended location codes by follow-up stock-location GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/stockpoints-v1` | `create_3` | Create stock point | `fortnox-api-tool stock-points create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse stock-point payload shape, and verifies by resolved response `id` plus read-back GET. |
| Shipped | `warehouse` | `DELETE` | `/api/warehouse/stockpoints-v1/{id}` | `delete` | Delete stock point | `fortnox-api-tool stock-points delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stockpoints-v1/{id}` | `getByAmbiguousId` | Get stock point | `fortnox-api-tool stock-points get` | Local unit-tested / live-unverified | Current shipped read keeps the documented code-or-id lookup path. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stockpoints-v1/{id}/stocklocations` | `getStockLocationsByAmbiguousId` | Get stock locations | `fortnox-api-tool stock-points get-stock-locations` | Local unit-tested / live-unverified | Current shipped read keeps the documented code-or-id lookup path and optional `q` filter. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stockpoints-v1` | `getAll_2` | List stock points | `fortnox-api-tool stock-points list` | Local unit-tested / live-unverified | Current shipped read keeps the documented `q` and `state` filters explicit. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stockpoints-v1/multi` | `getMany_3` | Get stock points | `fortnox-api-tool stock-points list-multi` | Local unit-tested / live-unverified | Current shipped read uses repeated `--id` flags and sends the documented comma-separated `ids` query plus optional `state`. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stockpoints-v1/{id}` | `update_3` | Update stock point | `fortnox-api-tool stock-points update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse stock-point payload shape, enforces `id` when present, and verifies selected read-back fields after the documented full-object update. |

### `stock-status` (1 operations)

- Official labels: `Stock Status`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `GET` | `/api/warehouse/status-v1/stockbalance` | `getStockBalance` | Get stock balance | `fortnox-api-tool stock-status get-stock-balance` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only and keeps the documented repeated `itemIds` and `stockPointCodes` filters explicit. |

### `stock-taking` (13 operations)

- Official labels: `Stock Taking`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/stocktaking-v1/{id}/rows` | `addStockTakingRows` | Add rows | `fortnox-api-tool stock-taking add-rows` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the documented raw top-level row array, and verifies row presence by follow-up row GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/stocktaking-v1/{id}/addrows` | `addStockTakingRowsByFilter` | Add rows by filter | `fortnox-api-tool stock-taking add-rows-by-filter` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the documented filter names explicit on the CLI, and verifies added rows by follow-up row GET. |
| Shipped | `warehouse` | `POST` | `/api/warehouse/stocktaking-v1` | `create_2` | Create stock taking | `fortnox-api-tool stock-taking create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, and verifies by resolved response `id` plus read-back GET. |
| Shipped | `warehouse` | `DELETE` | `/api/warehouse/stocktaking-v1/{id}` | `deleteStockTaking` | Delete Stock Taking document | `fortnox-api-tool stock-taking delete` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `warehouse` | `DELETE` | `/api/warehouse/stocktaking-v1/{id}/rows/{rowId}` | `deleteStockTakingRow` | Delete row | `fortnox-api-tool stock-taking delete-row` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies row absence by follow-up row GET. |
| Shipped | `warehouse` | `DELETE` | `/api/warehouse/stocktaking-v1/{id}/rows` | `deleteStockTakingRowByFilter` | Delete rows by filter | `fortnox-api-tool stock-taking delete-rows` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, keeps the documented filter names explicit on the CLI, and verifies removed row ids are absent on follow-up row GET when Fortnox returns them. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stocktaking-v1/{id}` | `get_2` | Get Stock Taking document | `fortnox-api-tool stock-taking get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stocktaking-v1/{id}/candidates` | `getCandidateRows` | Get candidate rows | `fortnox-api-tool stock-taking get-candidate-rows` | Local unit-tested / live-unverified | Current shipped read keeps the documented candidate-row filters explicit, including `includeNonInboundItems`. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stocktaking-v1/{id}/rows` | `getRows` | Get Stock Taking Rows | `fortnox-api-tool stock-taking get-rows` | Local unit-tested / live-unverified | Current shipped read keeps the documented row filters and row paging/sorting query names explicit. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stocktaking-v1` | `getAll_1` | List stock takings | `fortnox-api-tool stock-taking list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktaking-v1/{id}/release` | `release_2` | Release Stock Taking document | `fortnox-api-tool stock-taking release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies `state == completed` by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktaking-v1/{id}` | `update_2` | Update a stock taking | `fortnox-api-tool stock-taking update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the raw warehouse payload shape, enforces `id` when present, and verifies by read-back GET plus expected state match when `state` is supplied. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktaking-v1/{id}/void` | `voidStockTaking` | Void Stock Taking document | `fortnox-api-tool stock-taking void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies `state == voided` by follow-up GET. |

### `stock-transfers` (5 operations)

- Official labels: `Stock Transfer`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `POST` | `/api/warehouse/stocktransfer-v1` | `create_5` | Create a stock transfer document | `fortnox-api-tool stock-transfers create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the official raw warehouse payload shape, and verifies by resolved response `id` plus follow-up GET. |
| Shipped | `warehouse` | `GET` | `/api/warehouse/stocktransfer-v1/{id}` | `get_4` | Get stock transfer document | `fortnox-api-tool stock-transfers get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktransfer-v1/{id}/release` | `release_3` | Release a stock transfer document | `fortnox-api-tool stock-transfers release` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --plan-in` and verifies by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktransfer-v1/{id}` | `update_4` | Update a stock transfer document | `fortnox-api-tool stock-transfers update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the official raw warehouse payload shape, enforces `id` when present, and verifies by follow-up GET. |
| Shipped | `warehouse` | `PUT` | `/api/warehouse/stocktransfer-v1/{id}/void` | `voidStockTransfer` | Void a stock transfer document | `fortnox-api-tool stock-transfers void` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies by follow-up GET. |

### `supplier-invoice-accruals` (5 operations)

- Official labels: `Supplier Invoice Accruals`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/supplierinvoiceaccruals` | `SupplierInvoiceAccrualController_doCreate` | Create a supplier invoice accrual | `fortnox-api-tool supplier-invoice-accruals create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoiceaccruals/{SupplierInvoiceNumber}` | `SupplierInvoiceAccrualController_doShow` | Retrieve a single supplier invoice accrual | `fortnox-api-tool supplier-invoice-accruals get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoiceaccruals` | `SupplierInvoiceAccrualController_doIndex` | Retrieve a list of supplier invoice accruals | `fortnox-api-tool supplier-invoice-accruals list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/supplierinvoiceaccruals/{SupplierInvoiceNumber}` | `SupplierInvoiceAccrualController_doDelete` | Remove a supplier invoice accrual | `fortnox-api-tool supplier-invoice-accruals remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes --ack-irreversible` and verifies by follow-up absence check. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoiceaccruals/{SupplierInvoiceNumber}` | `SupplierInvoiceAccrualController_doUpdate` | Update a supplier invoice accrual | `fortnox-api-tool supplier-invoice-accruals update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `supplier-invoice-external-url-connections` (4 operations)

- Official labels: `Supplier Invoice External Url Connections`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/supplierinvoiceexternalurlconnections` | `SinvoiceExternalUrlConnectionController_doCreate` | Create a supplier invoice external URL connection | `fortnox-api-tool supplier-invoice-external-url-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, posts the documented flat request body, and verifies by resolved response `Id` plus follow-up GET. The rendered docs note the connection starts inactive until a supplier-invoice file connection exists. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoiceexternalurlconnections/{Id}` | `SinvoiceExternalUrlConnectionController_doShow` | Retrieve a single supplier invoice external URL connection | `fortnox-api-tool supplier-invoice-external-url-connections get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/supplierinvoiceexternalurlconnections/{Id}` | `SinvoiceExternalUrlConnectionController_doDelete` | Remove a supplier invoice external URL connection | `fortnox-api-tool supplier-invoice-external-url-connections remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoiceexternalurlconnections/{Id}` | `SinvoiceExternalUrlConnectionController_doUpdate` | Update a supplier invoice external URL connection | `fortnox-api-tool supplier-invoice-external-url-connections update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, keeps the documented flat request body, and verifies by follow-up GET on `Id`. |

### `supplier-invoice-file-connections` (4 operations)

- Official labels: `Supplier Invoice File Connections`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/supplierinvoicefileconnections` | `SupplierInvoiceFileConnectionController_doCreate` | Create an supplier invoice file connection | `fortnox-api-tool supplier-invoice-file-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies presence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoicefileconnections/{FileId}` | `SupplierInvoiceFileConnectionController_doShow` | Retrieve a single supplier invoice file connection | `fortnox-api-tool supplier-invoice-file-connections get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoicefileconnections` | `SupplierInvoiceFileConnectionController_doIndex` | Retrieve a list of supplier invoice file connections | `fortnox-api-tool supplier-invoice-file-connections list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/supplierinvoicefileconnections/{FileId}` | `SupplierInvoiceFileConnectionController_doDelete` | Remove an supplier invoice file connection | `fortnox-api-tool supplier-invoice-file-connections remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |

### `supplier-invoice-payments` (6 operations)

- Official labels: `Supplier Invoice Payments`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoicepayments/{Number}/bookkeep` | `SupplierInvoicePaymentController_doUpdateAndBookkeep` | Bookkeep a supplier invoice payment | `fortnox-api-tool supplier-invoice-payments bookkeep` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Booked == true` after write. |
| Shipped | `fortnox` | `POST` | `/3/supplierinvoicepayments` | `SupplierInvoicePaymentController_doCreate` | Create a supplier invoice payment | `fortnox-api-tool supplier-invoice-payments create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoicepayments/{Number}` | `SupplierInvoicePaymentController_doShow` | Retrieve a single supplier invoice payment | `fortnox-api-tool supplier-invoice-payments get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoicepayments` | `SupplierInvoicePaymentController_doIndex` | Retrieve a list of supplier invoice payments | `fortnox-api-tool supplier-invoice-payments list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/supplierinvoicepayments/{Number}` | `SupplierInvoicePaymentController_doDelete` | Remove a supplier invoice payment | `fortnox-api-tool supplier-invoice-payments remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires reviewed `--plan-in --yes --ack-irreversible` and verifies by follow-up absence check. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoicepayments/{Number}` | `SupplierInvoicePaymentController_doUpdate` | Update a supplier invoice payment | `fortnox-api-tool supplier-invoice-payments update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `supplier-invoices` (9 operations)

- Official labels: `Supplier Invoices`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}/approvalbookkeep` | `SupplierInvoiceController_doUpdateAndApprovalBookkeep` | Approval of bookkeep of given supplier invoice | `fortnox-api-tool supplier-invoices approvalbookkeep` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Booked == true` after write. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}/approvalpayment` | `SupplierInvoiceController_doUpdateAndApprovalPayment` | Approval of payment of given supplier invoice | `fortnox-api-tool supplier-invoices approvalpayment` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `PaymentPending == false` after write. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}/bookkeep` | `SupplierInvoiceController_doUpdateAndBookkeep` | Bookkeep given supplier invoice | `fortnox-api-tool supplier-invoices bookkeep` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Booked == true` after write. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}/cancel` | `SupplierInvoiceController_doUpdateAndCancel` | Cancels given supplier invoice | `fortnox-api-tool supplier-invoices cancel` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Cancelled == true` after write. |
| Shipped | `fortnox` | `POST` | `/3/supplierinvoices` | `SupplierInvoiceController_doCreate` | Create a supplier invoice | `fortnox-api-tool supplier-invoices create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies by read-back GET. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}/credit` | `SupplierInvoiceController_doUpdateAndCredit` | Credit given supplier invoice | `fortnox-api-tool supplier-invoices credit` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes` and verifies `Credit == true` with a present `CreditReference` after write. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoices/{GivenNumber}` | `SupplierInvoiceController_doShow` | Retrieve a single supplier invoice | `fortnox-api-tool supplier-invoices get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/supplierinvoices` | `SupplierInvoiceController_doIndex` | Retrieve a list of supplier invoices | `fortnox-api-tool supplier-invoices list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/supplierinvoices/{GivenNumber}` | `SupplierInvoiceController_doUpdate` | Update a supplier invoice | `fortnox-api-tool supplier-invoices update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `suppliers` (4 operations)

- Official labels: `Suppliers`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/suppliers` | `SupplierController_doCreate` | Create a supplier | `fortnox-api-tool suppliers create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/suppliers/{SupplierNumber}` | `SupplierController_doShow` | Retrieve a single supplier | `fortnox-api-tool suppliers get` | Local unit-tested / live-unverified | Current shipped read matches the rendered docs: path selector only, with no extra query params shown there. |
| Shipped | `fortnox` | `GET` | `/3/suppliers` | `SupplierController_doIndex` | Retrieve a list of suppliers | `fortnox-api-tool suppliers list` | Local unit-tested / live-unverified | Current shipped read keeps the rendered `suppliernumber`, `name`, `organisationnumber`, `phone`, `zipcode`, `city`, `email`, and `lastmodified` query params explicit. |
| Shipped | `fortnox` | `PUT` | `/3/suppliers/{SupplierNumber}` | `SupplierController_doUpdate` | Update a supplier | `fortnox-api-tool suppliers update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `tax-reductions` (5 operations)

- Official labels: `Tax Reductions`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/taxreductions` | `TaxReductionController_doCreate` | Create a Tax Reduction | `fortnox-api-tool tax-reductions create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, resolves `Id`, and verifies by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/taxreductions/{Id}` | `TaxReductionController_doShow` | Retrieve a single tax reduction | `fortnox-api-tool tax-reductions get` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/taxreductions` | `TaxReductionController_doIndex` | Retrieve a list of tax reductions | `fortnox-api-tool tax-reductions list` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `DELETE` | `/3/taxreductions/{Id}` | `TaxReductionController_doDelete` | Remove a tax reduction | `fortnox-api-tool tax-reductions remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in`, re-checks the payload hash, and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/taxreductions/{Id}` | `TaxReductionController_doUpdate` | Update a tax reduction | `fortnox-api-tool tax-reductions update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--plan-in`, re-checks the payload hash, enforces `TaxReduction.Id` when present, and verifies by follow-up GET. |

### `tenant` (1 operations)

- Official labels: `Tenant`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `warehouse` | `GET` | `/api/warehouse/tenants-v4` | `getTenant` | Get Warehouse activation status | `fortnox-api-tool tenant get` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only. |

### `terms-of-deliveries` (4 operations)

- Official labels: `Terms Of Deliveries`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/termsofdeliveries` | `TermsOfDeliveryController_doCreate` | Create a terms of delivery | `fortnox-api-tool terms-of-deliveries create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/termsofdeliveries/{Code}` | `TermsOfDeliveryController_doShow` | Retrieve a single terms of delivery | `fortnox-api-tool terms-of-deliveries get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/termsofdeliveries` | `TermsOfDeliveryController_doIndex` | Retrieve a list of terms of deliveries | `fortnox-api-tool terms-of-deliveries list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/termsofdeliveries/{Code}` | `TermsOfDeliveryController_doUpdate` | Update a terms of delivery | `fortnox-api-tool terms-of-deliveries update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `terms-of-payments` (5 operations)

- Official labels: `Terms Of Payments`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/termsofpayments` | `TermsOfPaymentController_doCreate` | Create a term of payment | `fortnox-api-tool terms-of-payments create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/termsofpayments/{Code}` | `TermsOfPaymentController_doShow` | Retrieve a single terms of payment | `fortnox-api-tool terms-of-payments get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/termsofpayments` | `TermsOfPaymentController_doIndex` | Retrieve a list of all terms of payments | `fortnox-api-tool terms-of-payments list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/termsofpayments/{Code}` | `TermsOfPaymentController_doDelete` | Remove a term of payment | `fortnox-api-tool terms-of-payments remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in --yes --ack-irreversible` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/termsofpayments/{Code}` | `TermsOfPaymentController_doUpdate` | Update a term of payment | `fortnox-api-tool terms-of-payments update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, re-checks the payload hash, and verifies by read-back GET. |

### `units` (5 operations)

- Official labels: `Units`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/units` | `UnitController_doCreate` | Create a unit | `fortnox-api-tool units create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, resolves `Code` from the response or payload, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/units/{Code}` | `UnitController_doShow` | Retrieve a single unit | `fortnox-api-tool units get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/units` | `UnitController_doIndex` | Retrieve a list of units | `fortnox-api-tool units list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/units/{Code}` | `UnitController_doDelete` | Remove a unit | `fortnox-api-tool units remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/units/{Code}` | `UnitController_doUpdate` | Update a unit | `fortnox-api-tool units update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `Unit.Code` when present, and verifies by read-back GET. |

### `users` (1 operations)

- Official labels: `Users`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `integration-developer` | `GET` | `/api/integration-developer/users/users-v1/{integrationId}/{tenantId}` | `getUsersForSingleIntegrationAndTenant` | Fetch user information for a single published integration and tenant | `fortnox-api-tool users fetch-user-information-for-a-single-published-integration-and-tenant` | Local unit-tested / live-unverified | Read-only. Current shipped read does the plain GET path only and keeps the documented array response shape intact. |

### `vacation-debt-basis` (1 operations)

- Official labels: `Vacation Debt Basis`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `GET` | `/3/vacationdebtbasis/{Year}/{Month}` | `VacationDebtBasisController_doShow` | Retrieve a specific vacation debt basis for a posted voucher | `fortnox-api-tool vacation-debt-basis get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `voucher-file-connections` (4 operations)

- Official labels: `Voucher File Connections`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/voucherfileconnections` | `VoucherFileConnectionController_doCreate` | Create a voucher file connection | `fortnox-api-tool voucher-file-connections create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in` and verifies presence by follow-up GET. |
| Shipped | `fortnox` | `GET` | `/3/voucherfileconnections/{FileId}` | `VoucherFileConnectionController_doShow` | Retrieve a single voucher file connection | `fortnox-api-tool voucher-file-connections get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/voucherfileconnections` | `VoucherFileConnectionController_doIndex` | Retrieve a list of voucher file connections | `fortnox-api-tool voucher-file-connections list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/voucherfileconnections/{FileId}` | `VoucherFileConnectionController_doDelete` | Remove a voucher file connection | `fortnox-api-tool voucher-file-connections remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |

### `voucher-series` (4 operations)

- Official labels: `Voucher Series`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/voucherseries` | `VoucherSeriesController_doCreate` | Create a voucher series | `fortnox-api-tool voucher-series create` | Local unit-tested / live-unverified |  |
| Shipped | `fortnox` | `GET` | `/3/voucherseries/{Code}` | `VoucherSeriesController_doShow` | Retrieve a single voucher series | `fortnox-api-tool voucher-series get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/voucherseries` | `VoucherSeriesController_doIndex` | Retrieve a list of voucher series | `fortnox-api-tool voucher-series list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `PUT` | `/3/voucherseries/{Code}` | `VoucherSeriesController_doUpdate` | Update a voucher series | `fortnox-api-tool voucher-series update` | Local unit-tested / live-unverified |  |

### `vouchers` (5 operations)

- Official labels: `Vouchers`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/vouchers` | `VoucherController_doCreate` | Create a voucher | `fortnox-api-tool vouchers create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`; use `--financial-year` when the voucher belongs to a specific year and verify by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/vouchers/{VoucherSeries}/{VoucherNumber}` | `VoucherController_doShow` | Retrieve a specific voucher | `fortnox-api-tool vouchers get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/vouchers` | `VoucherController_doIndex` | Retrieve all vouchers | `fortnox-api-tool vouchers list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/vouchers/sublist/{VoucherSeries}` | `VoucherController_doSublistWithParam` | Retrieve a list of vouchers for a specific series | `fortnox-api-tool vouchers list-by-series` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/vouchers/sublist` | `VoucherController_doSubList` | Retrieve all vouchers for the current financial year | `fortnox-api-tool vouchers list-current-financial-year` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |

### `way-of-deliveries` (5 operations)

- Official labels: `Way Of Deliveries`
- Family status: **Shipped**

| Status | Group | HTTP | Path | Operation ID | Title | Planned CLI command | Proof status | Notes |
|---|---|---|---|---|---|---|---|---|
| Shipped | `fortnox` | `POST` | `/3/wayofdeliveries` | `WayOfDeliveryController_doCreate` | Create a way of delivery | `fortnox-api-tool way-of-deliveries create` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, resolves `Code` from the response or payload, and verifies by read-back GET. |
| Shipped | `fortnox` | `GET` | `/3/wayofdeliveries/{Code}` | `WayOfDeliveryController_doShow` | Retrieve a single way of delivery | `fortnox-api-tool way-of-deliveries get` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `GET` | `/3/wayofdeliveries` | `WayOfDeliveryController_doIndex` | Retrieve a list of way of deliveries | `fortnox-api-tool way-of-deliveries list` | Local unit-tested / live-unverified | Current shipped read does the plain GET path only. |
| Shipped | `fortnox` | `DELETE` | `/3/wayofdeliveries/{Code}` | `WayOfDeliveryController_doDelete` | Remove a way of delivery | `fortnox-api-tool way-of-deliveries remove` | Local unit-tested / live-unverified | Dry-run by default. Apply requires `--yes --ack-no-snapshot --ack-irreversible --plan-in` and verifies absence by follow-up GET. |
| Shipped | `fortnox` | `PUT` | `/3/wayofdeliveries/{Code}` | `WayOfDeliveryController_doUpdate` | Update a way of delivery | `fortnox-api-tool way-of-deliveries update` | Local unit-tested / live-unverified | Dry-run by default. Apply requires a reviewed `--plan-in`, enforces `WayOfDelivery.Code` when present, and verifies by read-back GET. |

## Websocket control commands

| Status | Official command | Planned CLI command | Notes |
|---|---|---|---|
| Shipped | `add-tenants-v1` | `fortnox-api-tool ws tenants add` | Adds new tenants to the websocket stream. Official payload includes includeChildTenants, clientSecret, and accessTokens. |
| Shipped | `remove-tenants-v1` | `fortnox-api-tool ws tenants remove` | Removes tenants from the websocket stream. |
| Shipped | `list-tenants-v1` | `fortnox-api-tool ws tenants list` | Lists tenants already added for subscription. |
| Shipped | `add-topics-v1` | `fortnox-api-tool ws topics add` | Adds topics with optional replay offsets. Official docs say offsets can replay up to 14 days back. |
| Shipped | `subscribe-v1` | `fortnox-api-tool ws subscribe start` | Starts the subscription after tenants and topics are set. |

## Websocket topics and events

- Official websocket stream URL: `wss://ws.fortnox.se/topics-v1`
- Events are minimal in payload; official docs tell clients to look up the entity for more information.
- Official docs say topic replay offsets can replay events up to 14 days back.

| Status | Topic | Events | Planned CLI command | Documented event names | Notes |
|---|---|---:|---|---|---|
| Shipped | `articles` | 3 | `fortnox-api-tool ws topics add --topic articles` | `article-created-v1`, `article-updated-v1`, `article-deleted-v1` |  |
| Shipped | `bureau-activities` | 2 | `fortnox-api-tool ws topics add --topic bureau-activities` | `activity-created-v1`, `activity-updated-v1` |  |
| Shipped | `bureau-assignments` | 3 | `fortnox-api-tool ws topics add --topic bureau-assignments` | `assignment-created-v1`, `assignment-updated-v1`, `assignment-deleted-v1` |  |
| Shipped | `cost-centers` | 3 | `fortnox-api-tool ws topics add --topic cost-centers` | `cost-center-created-v1`, `cost-center-updated-v1`, `cost-center-deleted-v1` |  |
| Shipped | `currencies` | 3 | `fortnox-api-tool ws topics add --topic currencies` | `currency-created-v1`, `currency-updated-v1`, `currency-deleted-v1` |  |
| Shipped | `customers` | 3 | `fortnox-api-tool ws topics add --topic customers` | `customer-created-v1`, `customer-updated-v2`, `customer-deleted-v1` | Official docs currently mix v1 and v2 event suffixes in this topic; keep the exact documented event names. |
| Shipped | `financial-years` | 6 | `fortnox-api-tool ws topics add --topic financial-years` | `financial-year-created-v1`, `financial-year-updated-v1`, `financial-year-deleted-v1`, `account-created-v1`, `account-updated-v1`, `account-deleted-v1` |  |
| Shipped | `invoices` | 7 | `fortnox-api-tool ws topics add --topic invoices` | `invoice-created-v1`, `invoice-updated-v1`, `invoice-cancelled-v1`, `invoice-bookkeep-v1`, `invoicepayment-bookkeep-v1`, `invoicepayment-deleted-v1`, `reminder-sent-v1` |  |
| Shipped | `messages` | 1 | `fortnox-api-tool ws topics add --topic messages` | `send-push-notification-queued-v1` |  |
| Shipped | `offers` | 3 | `fortnox-api-tool ws topics add --topic offers` | `offer-created-v1`, `offer-updated-v1`, `offer-canceled-v1` |  |
| Shipped | `orders` | 3 | `fortnox-api-tool ws topics add --topic orders` | `order-created-v1`, `order-updated-v1`, `order-cancelled-v1` |  |
| Shipped | `projects` | 3 | `fortnox-api-tool ws topics add --topic projects` | `project-created-v1`, `project-updated-v1`, `project-deleted-v1` |  |
| Shipped | `supplier-invoices` | 4 | `fortnox-api-tool ws topics add --topic supplier-invoices` | `supplier-invoice-created-v1`, `supplier-invoice-updated-v1`, `supplier-invoice-cancelled-v1`, `supplier-invoice-bookkeep-v1` |  |
| Shipped | `suppliers` | 3 | `fortnox-api-tool ws topics add --topic suppliers` | `supplier-created-v1`, `supplier-updated-v1`, `supplier-deleted-v1` |  |
| Shipped | `termsofdeliveries` | 3 | `fortnox-api-tool ws topics add --topic termsofdeliveries` | `termofdelivery-created-v1`, `termofdelivery-updated-v1`, `termofdelivery-deleted-v1` |  |
| Shipped | `termsofpayments` | 3 | `fortnox-api-tool ws topics add --topic termsofpayments` | `termsofpayments-created-v1`, `termsofpayments-updated-v1`, `termsofpayments-deleted-v1` |  |
| Shipped | `vouchers` | 3 | `fortnox-api-tool ws topics add --topic vouchers` | `voucher-created-v1`, `voucher-updated-v1`, `voucher-deleted-v1` |  |
| Shipped | `warehouse-stockbalances` | 1 | `fortnox-api-tool ws topics add --topic warehouse-stockbalances` | `warehouse-stockbalance-changed-v1` |  |
| Shipped | `waysofdeliveries` | 3 | `fortnox-api-tool ws topics add --topic waysofdeliveries` | `waysofdeliveries-created-v1`, `waysofdeliveries-updated-v1`, `waysofdeliveries-deleted-v1` |  |

## Honest gaps still open

- The documented read query/filter coverage is now aligned with the rendered Fortnox docs for the shipped surface, but the live behavior of those reads is still unverified from this workspace.
- Websocket controls and the subscribe flow are unit-tested locally but still live-unverified against real Fortnox credentials from this workspace.
- Final live REST proof is still pending in this workspace because local Fortnox credentials were not present during the latest validation pass.
- Direct OpenAPI download still needs a clean retrieval path if we want a second independent official snapshot beyond the rendered docs page.
