# API coverage

This is the shipped scope ledger for the runtime in this folder.

## Source summary

- Provider: Salesforce Platform REST API plus Bulk API 2.0 under `/services/data`
- Auth method: OAuth 2.0 bearer token
- Docs baseline used for implementation: official Salesforce REST API `67.0` and Bulk API 2.0 `67.0` PDFs verified locally on `2026-05-26`
- Default API version in the tool: `67.0`
- Shipped command count: `175`

## Included scope

| REST area | Shipped CLI families | Notes |
|---|---|---|
| Core discovery and org information | `versions`, `resources`, `openapi-sobjects`, `limits`, `record-count`, `tabs`, `themes`, `app-menu`, `compact-layouts` | Includes the sObjects OpenAPI generation beta. |
| Query and search | `query`, `query-all`, `search`, `parameterized-search`, `recent` | Less common query parameters can still be passed with `--query-param`. |
| sObject metadata and rows | `sobjects-global`, `sobjects-object`, `sobjects-describe`, `sobjects-deleted`, `sobjects-updated`, `sobjects-named-layouts`, `sobjects-row`, `sobjects-event-series`, `sobjects-external-id`, `sobjects-blob` | Multipart blob upload is supported on the documented write paths with `--multipart-file`. |
| sObject advanced resources | `sobjects-approval-layouts`, `sobjects-approval-process`, `sobjects-compact-layouts`, `sobjects-layouts`, `sobjects-layouts-record-type`, `sobjects-global-layouts`, `sobjects-platform-actions`, `sobjects-quick-actions`, `sobjects-quick-action`, `sobjects-quick-action-describe`, `sobjects-quick-action-defaults`, `sobjects-quick-action-defaults-context`, `sobjects-rich-text-image`, `sobjects-relationships`, `sobjects-suggested-articles`, `sobjects-suggested-articles-id`, `sobjects-user-password`, `sobjects-self-service-user-password`, `sobjects-relevant-items`, `sobjects-lightning-metrics`, `platform-events` | Some families are feature- or org-gated. |
| Support, Knowledge, consent, and Named Query | `support`, `knowledge`, `consent`, `embedded-service`, `named-query`, `portability` | Knowledge endpoints often need `--header Accept-Language=...`. |
| Actions, list views, process, product schedules, scheduler, surveys | `actions`, `actions-custom`, `actions-standard`, `listviews`, `process-approvals`, `process-rules`, `process-rule`, `process-object-rules`, `product-schedules`, `quick-actions`, `scheduler`, `surveys-translation` | Scheduler, surveys, and some action targets are org-gated. |
| Composite | `composite`, `composite-graph`, `composite-batch`, `composite-tree`, `composite-collections` | Collections writes also support multipart blob upload. |
| Bulk API 2.0 jobs | `jobs-ingest`, `jobs-query` | Includes create, state changes, list, result download, and query result-page discovery. |

## Explicitly excluded scope

These resources were left out on purpose because the official Salesforce REST resource table points them to separate product guides, separate APIs, or internal-only usage.

- Analytics and related resources: `analytics`, `wave`, `folders`, `jsonxform`, `smartdatadiscovery`, `eclair`
- Connect and Chatter families: `connect`, `chatter`, `dedupe`, `asset-management`, industry `connect/*` families
- Commerce and non-core product families: `commerce`, `contact-tracing`, Field Service support subresources
- Platform-adjacent but separate APIs: `metadata`, `tooling`, `ui-api`, Streaming API push
- Internal-only or provider-internal resources: `domino`, `emailConnect`, `licensing`, `payments`, `serviceTemplates`

## Runtime action inventory

- `versions`: `list`
- `resources`: `list`
- `openapi-sobjects`: `list-selectors`, `create`, `details`, `results`
- `limits`: `list`, `record-count`
- `query`: `run`, `more`, `explain`
- `query-all`: `run`, `more`
- `search`: `sosl`, `scope-order`, `layouts`, `autocomplete`, `suggested-title`, `suggested-queries`
- `parameterized-search`: `get`, `post`
- `recent`: `list`
- `record-count`: `list`
- `tabs`: `list`, `headers`
- `themes`: `list`
- `app-menu`: `types`, `items`, `mobile-items`
- `compact-layouts`: `list`
- `sobjects-global`: `describe`
- `sobjects-object`: `get`, `create`, `headers`
- `sobjects-describe`: `get`
- `sobjects-deleted`: `get`
- `sobjects-updated`: `get`
- `sobjects-named-layouts`: `get`
- `sobjects-row`: `get`, `update`, `delete`
- `sobjects-event-series`: `delete`
- `sobjects-external-id`: `get`, `create`, `upsert`, `delete`, `headers`
- `sobjects-blob`: `get`
- `sobjects-approval-layouts`: `list`, `headers`
- `sobjects-approval-process`: `get`, `headers`
- `sobjects-compact-layouts`: `list`, `headers`
- `sobjects-layouts`: `list`, `headers`
- `sobjects-layouts-record-type`: `get`, `headers`
- `sobjects-global-layouts`: `list`, `headers`
- `sobjects-platform-actions`: `query`
- `sobjects-quick-actions`: `list`, `headers`
- `sobjects-quick-action`: `get`, `create`, `headers`
- `sobjects-quick-action-describe`: `get`, `headers`
- `sobjects-quick-action-defaults`: `get`, `headers`
- `sobjects-quick-action-defaults-context`: `get`, `headers`
- `sobjects-rich-text-image`: `get`
- `sobjects-relationships`: `get`, `update`, `delete`
- `sobjects-suggested-articles`: `get`
- `sobjects-suggested-articles-id`: `get`
- `sobjects-user-password`: `status`, `set`, `reset`, `headers`
- `sobjects-self-service-user-password`: `status`, `set`, `reset`, `headers`
- `sobjects-relevant-items`: `get`
- `sobjects-lightning-metrics`: `toggle`, `app-type`, `browser`, `page`, `flexipage`, `exit-page`
- `platform-events`: `schema-by-name`, `schema-by-id`
- `support`: `root`, `data-category-groups`, `data-category-detail`, `knowledge-articles`, `knowledge-article`
- `knowledge`: `settings`
- `consent`: `compile`, `multiaction`, `data360-read`, `write`, `data360-write`
- `embedded-service`: `get`, `headers`
- `actions`: `list`, `headers`
- `actions-custom`: `list`, `headers`
- `actions-standard`: `list`, `headers`
- `listviews`: `object-list`, `basic`, `describe`, `results`, `recent`
- `named-query`: `get`
- `portability`: `create`, `status`
- `process-approvals`: `list`, `act`, `headers`
- `process-rules`: `list`, `trigger`, `headers`
- `process-rule`: `get`, `trigger`, `headers`
- `process-object-rules`: `list`, `headers`
- `product-schedules`: `get`, `create`, `delete`
- `quick-actions`: `list`, `create`, `headers`
- `scheduler`: `slots`, `candidates`
- `surveys-translation`: `upsert`, `get`, `delete`, `upsert-multi`, `delete-multi`, `get-multi`
- `composite`: `list`, `execute`
- `composite-graph`: `execute`
- `composite-batch`: `execute`
- `composite-tree`: `create`
- `composite-collections`: `create`, `get`, `get-body`, `update`, `upsert`, `delete`
- `jobs-ingest`: `create`, `upload`, `upload-complete`, `get`, `successful-results`, `failed-results`, `unprocessed`, `delete`, `abort`, `list`
- `jobs-query`: `create`, `get`, `results`, `result-pages`, `delete`, `abort`, `list`

## Known gaps and live-unverified areas

- Nested execution subtrees below `/actions/custom/*` and `/actions/standard/*` are not shipped as generic runtime commands here. The main REST guide documents the roots and one product-specific Data Kit flow example, but not a stable general Platform REST action execution surface for every subtype.
- `/services/data/vXX.X/sobjects/StreamingChannel/{channelId}/push` is intentionally excluded because the resource table routes it to the separate Streaming API guide.
- Some supported families are feature-gated or org-gated in Salesforce. In this environment they remain live-unverified until a real org proves them. See `docs/proof.md`.
