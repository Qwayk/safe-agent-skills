# Command reference

This is the shipped command guide for people who want exact syntax.

If you want help deciding what to ask for first, start with [What this skill can help you do](use_cases.md), [Set up your account step by step](onboarding.md), and [See how this skill keeps changes safe](safety_model.md).

## Get connected

Use these commands to create local setup files or check basic runtime details.

- `wix-safe-agent-cli onboarding [--no-write-env]`
- `wix-safe-agent-cli --output json --version`

## Check access

Use these commands to confirm the tool can reach the account safely.

- `wix-safe-agent-cli auth check`
- `wix-safe-agent-cli auth token create`
- `wix-safe-agent-cli auth token request --code <authorization-code>`
- `wix-safe-agent-cli auth token refresh [--refresh-token <token>]`
- `wix-safe-agent-cli auth token inspect --token <token>`
- `wix-safe-agent-cli auth token set --file token.json`
- `wix-safe-agent-cli auth token status`

Notes for OAuth token helpers:
- `auth token request` uses the official legacy `POST /oauth/access` authorization-code flow.
- Wix marks `auth token request` and `auth token refresh` deprecated for new apps. This CLI keeps them only for existing legacy custom-auth app setups.
- `auth token request` stores the returned token JSON under the local `.state/token.json` and never prints raw token values.

## Read app install state

Use these commands to inspect installed-app state on the current site context.

- `wix-safe-agent-cli app-instance get`
- `wix-safe-agent-cli embedded-scripts get [--component-id <id>]`
- `wix-safe-agent-cli site-plugins get-placement-status`

## Send BI events

Use this command to send an explicit Wix app BI event.

- `wix-safe-agent-cli --plan-out plan.json bi-event send --event-name <name> [--event-data-json '{"key":"value"}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bi-event send --event-name <name> [--event-data-json '{"key":"value"}'] [--receipt-out receipt.json]`

Notes for BI Event:
- `bi-event send` uses the official `POST /apps/v1/bi-event` method.
- This is a reviewed-plan write because the event cannot be unsent.
- The command requires `--event-name` and accepts optional JSON `eventData` through `--event-data-json`.
- Verification is provider-response only. A successful receipt means Wix accepted the POST, not that a later setup or analytics side effect is fully proven here.

## Manage embedded scripts

Use these commands to inspect or apply the current embedded script state for this app.

- `wix-safe-agent-cli embedded-scripts get [--component-id <id>]`
- `wix-safe-agent-cli --plan-out plan.json embedded-scripts embed [--component-id <id>] [--disabled true|false] [--parameters-json '{"key":"value"}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json embedded-scripts embed [--component-id <id>] [--disabled true|false] [--parameters-json '{"key":"value"}'] [--receipt-out receipt.json]`

## Search app market listings

Use this command to find published Wix App Market listings by keyword or app name.

- `wix-safe-agent-cli market-listing search --search-term <text> [--language-code <code>] [--limit N]`

Notes for Market Listing:
- `market-listing search` is read-only in this boundary.
- The method page does not list a narrower identity restriction. In this CLI it runs through the existing app or stored-access-token path.
- The official method docs mark it Developer Preview.
- The search returns published listings only, defaults to English, and keeps the result size explicit with `--limit` up to 50 per page.

## Generate editor deep links

Use this command to generate a Wix editor link for the app's legacy custom element flow.

- `wix-safe-agent-cli editor-deep-link create [--custom-params-json '{"key":"value"}']`

Notes for Editor Deep Link:
- `editor-deep-link create` is a helper POST in this boundary, not a destructive live write.
- It uses the official `POST /apps/v1/post-installation/editor-deep-link` method.
- The official method page requires permission `Manage Your App`.
- The intro says this API works only with the legacy custom element.
- Omit `--custom-params-json` to generate a plain editor-opening link. When you pass it, values must be string key/value pairs.
- This family is locally proven and live-unverified; proof is based on mocked request and parser coverage.

Notes for App Management reads:
- `app-instance get`, `embedded-scripts get`, and `site-plugins get-placement-status` are read-only commands in this boundary.
- These commands use Wix app or Wix user identity auth for the installed site context.
- `embedded-scripts get` uses the official `GET /apps/v1/scripts` method. Pass `--component-id` only when your app has more than one embedded script component.
- The Embedded Scripts family intro says to authenticate as a Wix App, while the get-method page says Wix app or Wix user identity. This tool keeps that docs mismatch explicit and remains live-unverified.
- `site-plugins get-placement-status` uses the official `GET /app-plugins/v1/site-plugins/placement-status` method.
- This family uses permission `Read Site Plugin Status`.
- This family is locally proven and live-unverified; proof is based on mocked request and parser coverage.

Notes for Embedded Scripts writes:
- `embedded-scripts embed` uses the official `POST /apps/v1/scripts` method.
- This is a reviewed-plan write: dry-run first with `--plan-out`, then live apply only with `--plan-in --apply --yes`.
- The plan captures the current embedded script state by rerunning `embedded-scripts get` before apply.
- If your app has more than one embedded script component, pass `--component-id`. If it has only one, omit it to match the official Wix guidance.
- `--parameters-json` must be a JSON object with string keys and string values only.
- Verification is a read-after-write check on the embedded script state, not a claim that the script already ran on a live site.

## Read and manage Wix Events settings

- `wix-safe-agent-cli events-settings get`
- `wix-safe-agent-cli --plan-out plan.json events-settings update --events-settings-id <events_settings_id> --settings-json @settings.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-settings update --events-settings-id <events_settings_id> --settings-json @settings.json [--receipt-out receipt.json]`

Notes for Events Settings:
- `events-settings get` is a read command for the current Wix Events & Tickets app settings.
- `events-settings update` is a reviewed-plan write.
- Official Wix docs mark Update Events Settings as Developer Preview.
- Official Wix docs say the Wix Events & Tickets app must be installed.
- Official Wix docs say this family requires `Manage Events`.
- Official Wix docs say most settings are read-only and only specific payment-related settings can be updated directly through the API.
- This family remains live-unverified.

## Read and manage Wix Portfolio settings

- `wix-safe-agent-cli portfolio-settings get`
- `wix-safe-agent-cli --plan-out plan.json portfolio-settings update --settings-json @settings.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-settings update --settings-json @settings.json [--receipt-out receipt.json]`

Notes for Portfolio Settings:
- `portfolio-settings get` is a read command for the current Wix Portfolio app settings.
- `portfolio-settings update` is a reviewed-plan write.
- Official Wix docs say the Wix Portfolio app must be installed.
- Official Wix docs say each site has one portfolio settings record, created automatically when the Portfolio app is installed.
- Official Wix docs say this family requires `Manage Portfolio`.
- Official Wix docs say the existing `revision` must be passed when updating. This command reads the current settings first, fills the current revision into `--settings-json` when missing, and refuses mismatched revisions.
- Apply captures before-state and verifies by rereading Portfolio Settings after the update.
- Portfolio Settings Created is a webhook/event surface, not a CLI command.
- This family remains live-unverified.

## Manage Wix Portfolio collections

- `wix-safe-agent-cli portfolio-collections list [--params-json '{}']`
- `wix-safe-agent-cli portfolio-collections get --collection-id <collection_id> [--params-json '{}']`
- `wix-safe-agent-cli portfolio-collections query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-collections create --collection-json @collection.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-collections create --collection-json @collection.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-collections update --collection-id <collection_id> --collection-json @collection.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-collections update --collection-id <collection_id> --collection-json @collection.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-collections delete --collection-id <collection_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json portfolio-collections delete --collection-id <collection_id> [--receipt-out receipt.json]`

Notes for Portfolio Collections:
- Official Wix docs say this API works only on sites where the Wix Portfolio app is installed.
- Official Wix docs do not show a clear auth block on every Collections method page. This tool uses the same Wix app or Wix user identity path as the shipped Portfolio Settings commands.
- The rendered get/list/query and event pages currently show an unrelated-looking permission label, `Wix Multilingual - Nile Wrapper Domain Events Read`; this is kept as an official-docs mismatch until Wix clarifies it.
- Query returns up to `100` collections per request and defaults to `id ASC`.
- Documented query fields include `id`, `title`, `description`, `slug`, `sortOrder`, `hidden`, `createdDate`, and `updatedDate`.
- Official Wix docs say the existing `revision` must be passed when updating. This command reads the current collection first, fills the current revision into `--collection-json` when missing, and refuses mismatched revisions.
- `delete` is a reviewed-plan write and also requires `--ack-irreversible`.
- Collection Created, Collection Updated, and Collection Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Portfolio projects

- `wix-safe-agent-cli portfolio-projects list [--params-json '{}']`
- `wix-safe-agent-cli portfolio-projects get --project-id <project_id> [--params-json '{}']`
- `wix-safe-agent-cli portfolio-projects query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-projects create --project-json @project.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-projects create --project-json @project.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-projects update --project-id <project_id> --project-json @project.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-projects update --project-id <project_id> --project-json @project.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-projects bulk-update --projects-json @projects.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-projects bulk-update --projects-json @projects.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-projects delete --project-id <project_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json portfolio-projects delete --project-id <project_id> [--receipt-out receipt.json]`

Notes for Portfolio Projects:
- Official Wix docs say this API works only on sites where the Wix Portfolio app is installed.
- Cover images and videos must first be uploaded or imported through Wix Media Manager before their media IDs can be used on projects.
- Official Wix docs say this family can be called as a Wix app or Wix user identity and requires `Manage Portfolio`.
- Query returns up to `100` projects per request and defaults to `id ASC`.
- Documented query fields include `id`, `title`, `description`, `slug`, `collectionIds`, `hidden`, `createdDate`, and `updatedDate`.
- Official Wix docs say the existing `revision` must be passed when updating. Update and bulk update read current projects first, fill current revisions when missing, and refuse mismatched revisions.
- The CLI keeps the rendered official bulk update path exactly as Wix currently shows it: `/portfolio/projects/projects/api/v1/bulk/portfolio/projects/update`.
- `delete` is a reviewed-plan write and also requires `--ack-irreversible`.
- Project Created, Project Updated, and Project Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Portfolio project items

- `wix-safe-agent-cli portfolio-project-items list --project-id <project_id> [--params-json '{}']`
- `wix-safe-agent-cli portfolio-project-items get --item-id <item_id> [--params-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items create --item-json @item.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-project-items create --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items update --item-id <item_id> --item-json @item.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-project-items update --item-id <item_id> --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items bulk-create --items-json @items.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-project-items bulk-create --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items bulk-update --items-json @items.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-project-items bulk-update --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items duplicate --duplicate-json @duplicate.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json portfolio-project-items duplicate --duplicate-json @duplicate.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items delete --item-id <item_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json portfolio-project-items delete --item-id <item_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json portfolio-project-items bulk-delete --item-ids-json @item-ids.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json portfolio-project-items bulk-delete --item-ids-json @item-ids.json [--receipt-out receipt.json]`

Notes for Portfolio Project Items:
- Official Wix docs say this API works only on sites where the Wix Portfolio app is installed.
- Project items are images or videos inside an existing project, so create, list, and duplicate work need existing project IDs.
- Images and videos must first be uploaded or imported through Wix Media Manager before their media IDs can be used on project items.
- The create, bulk create, and duplicate pages say this family can be called as a Wix app or Wix user identity and requires `Manage Portfolio`.
- Current get/list/event pages show an unrelated-looking permission label, `Wix Multilingual - Nile Wrapper Domain Events Read`, and several write pages omit a clear auth block. This tool keeps that official-docs mismatch explicit and uses the same Portfolio app/user auth path as the neighboring Portfolio commands.
- The Project Item object page does not show a `revision` field. Update and bulk update still read current items first for before-state and verify with read-after-write, but they do not synthesize revisions.
- `list` retrieves all project items for one project. The current official page does not show paging, filter, or sort controls.
- `delete` and `bulk-delete` are reviewed-plan writes and also require `--ack-irreversible`.
- Project Item Created, Project Item Updated, and Project Item Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Suppliers Hub products

- `wix-safe-agent-cli suppliers-hub-products get --product-id <product_id>`
- `wix-safe-agent-cli suppliers-hub-products query --query-json @query.json`
- `wix-safe-agent-cli suppliers-hub-products search --search-json @search.json`
- `wix-safe-agent-cli suppliers-hub-products query-categories --query-json @query.json`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products create --product-json @product.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products create --product-json @product.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products update --product-id <product_id> --product-json @product.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products update --product-id <product_id> --product-json @product.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-create --products-json @products.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products bulk-create --products-json @products.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-update --products-json @products.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products bulk-update --products-json @products.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-add-to-store --add-json @add.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products bulk-add-to-store --add-json @add.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-update-tags --tags-json @tags.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-products bulk-update-tags --tags-json @tags.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-update-tags-by-filter --tags-json @tags.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-products bulk-update-tags-by-filter --tags-json @tags.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products delete --product-id <product_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-products delete --product-id <product_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-products bulk-delete --product-ids-json @product-ids.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-products bulk-delete --product-ids-json @product-ids.json [--receipt-out receipt.json]`

Notes for Suppliers Hub Products:
- Official Wix docs mark this API Developer Preview and say it is available only to approved Wix business partners with a signed business agreement.
- Products can be dropshipping, wholesale, print-on-demand, or supported combinations. The first image in `media.items` becomes the main image.
- The product object has no `revision` field. Update, bulk update, and tag update still read current products first for before-state and verify with read-after-write when the command targets known product IDs.
- `query` is the strongly consistent operational read. `search` is eventually consistent and meant for catalog discovery with text search and aggregations.
- Bulk create, update, delete, and tag update methods can return partial success through `itemMetadata`, so receipts keep the provider response for per-item review.
- `bulk-update-tags-by-filter` is asynchronous and can touch many products, including all products when the filter is empty, so it also requires `--ack-irreversible`. The command verifies returned job creation only; inspect progress with `async-jobs`.
- The Bulk Add Products To Store page currently shows a generated endpoint under `/suppliershub/marketplace-product/v1/...` but the curl example uses `/suppliers-hub/v1/...`; this CLI uses the generated Method API Endpoint and documents that mismatch.
- Product Created, Product Deleted, Product Tags Modified, and Product Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Suppliers Hub suppliers

- `wix-safe-agent-cli suppliers-hub-suppliers get --supplier-id <supplier_id>`
- `wix-safe-agent-cli suppliers-hub-suppliers query --query-json @query.json`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers create --supplier-json @supplier.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-suppliers create --supplier-json @supplier.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers update --supplier-id <supplier_id> --supplier-json @supplier.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-suppliers update --supplier-id <supplier_id> --supplier-json @supplier.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers bulk-create --suppliers-json @suppliers.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-suppliers bulk-create --suppliers-json @suppliers.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers bulk-update --suppliers-json @suppliers.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-suppliers bulk-update --suppliers-json @suppliers.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers bulk-update-tags --tags-json @tags.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-suppliers bulk-update-tags --tags-json @tags.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers bulk-update-tags-by-filter --tags-json @tags.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-suppliers bulk-update-tags-by-filter --tags-json @tags.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers delete --supplier-id <supplier_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-suppliers delete --supplier-id <supplier_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-suppliers bulk-delete --supplier-ids-json @supplier-ids.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json suppliers-hub-suppliers bulk-delete --supplier-ids-json @supplier-ids.json [--receipt-out receipt.json]`

Notes for Suppliers Hub Suppliers:
- Official Wix docs mark this API Developer Preview and say it is available only to approved Wix business partners with a signed business agreement.
- Supplier updates require the current `revision`. The CLI reads the supplier first, injects the current revision when omitted, and refuses a provided revision that does not match Wix before-state.
- Bulk update also reads each supplier first and applies the same revision guard to every supplier entry.
- Bulk create, update, delete, and tag update methods can return partial success through `itemMetadata`, so receipts keep the provider response for per-item review.
- `bulk-update-tags-by-filter` is asynchronous and can touch all suppliers when the filter is empty, so it also requires `--ack-irreversible`. The command verifies returned job creation only; inspect progress with `async-jobs`.
- Supplier Created, Supplier Deleted, Supplier Tags Modified, and Supplier Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Submit Wix Suppliers Hub Marketplace provider results

- `wix-safe-agent-cli --plan-out plan.json suppliers-hub-marketplace-provider-submissions submit-generated-mockups --mockups-json @mockups.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json suppliers-hub-marketplace-provider-submissions submit-generated-mockups --mockups-json @mockups.json [--receipt-out receipt.json]`

Notes for Suppliers Hub Marketplace Provider Submissions:
- Official Wix docs mark this API Developer Preview and describe it as a provider-backend reporting API for asynchronous mockup generation results.
- Each request can contain up to 100 `mockups`. Each mockup must include `providerProductId`, `imageType`, and `status`; `COMPLETED` mockups must include `mockupUrl`.
- Wix keys mockups by authenticated provider, `providerProductId`, and `imageType`; no `appId` is passed in the request body.
- The Submit Generated Mockups page currently shows a generated endpoint under `/suppliershub/v2/...` but the curl example uses `/suppliers-hub/marketplace-provider-host/v2/...`; this CLI uses the generated Method API Endpoint and documents that mismatch.
- This family remains live-unverified.

## Manage Wix Events V3 events

- `wix-safe-agent-cli events-v3 get --event-id <event_id>`
- `wix-safe-agent-cli events-v3 query --query-json @query.json`
- `wix-safe-agent-cli events-v3 count-by-status [--query-json @query.json]`
- `wix-safe-agent-cli events-v3 get-by-slug --slug <event_slug>`
- `wix-safe-agent-cli events-v3 list-by-category --category-id <category_id>`
- `wix-safe-agent-cli --plan-out plan.json events-v3 create --event-json @event.json`
- `wix-safe-agent-cli --plan-out plan.json events-v3 update --event-id <event_id> --event-json @event.json`
- `wix-safe-agent-cli --plan-out plan.json events-v3 clone --event-id <event_id> [--request-json @clone.json]`
- `wix-safe-agent-cli --plan-out plan.json events-v3 publish-draft --event-id <event_id> [--request-json @publish.json]`
- `wix-safe-agent-cli --plan-out plan.json events-v3 cancel --event-id <event_id> [--request-json @cancel.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-v3 cancel --event-id <event_id> [--request-json @cancel.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-v3 delete --event-id <event_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-v3 delete --event-id <event_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-v3 bulk-cancel-by-filter --filter-json @filter.json`
- `wix-safe-agent-cli --plan-out plan.json events-v3 bulk-delete-by-filter --filter-json @filter.json`

Notes for Events V3:
- `get`, `query`, `count-by-status`, `get-by-slug`, and `list-by-category` are reads/helpers. Official Wix docs mark `list-by-category` as Developer Preview.
- `create`, `update`, `clone`, and `publish-draft` are reviewed-plan writes.
- `cancel`, `bulk-cancel-by-filter`, `delete`, and `bulk-delete-by-filter` also require `--ack-irreversible`.
- Official Wix docs say the Wix Events & Tickets app must be installed.
- Official Wix docs say reads need `Read Events`; writes need `Manage Events`.
- Official Wix docs say canceled events close registration and may send cancellation notifications.
- Official Wix docs say deleted events can be retrieved only through a GDPR access request.
- This family remains live-unverified.

## Manage Wix Events Ticket Definitions V3

- `wix-safe-agent-cli events-ticket-definitions-v3 get --ticket-definition-id <ticket_definition_id>`
- `wix-safe-agent-cli events-ticket-definitions-v3 query [--query-json @query.json]`
- `wix-safe-agent-cli events-ticket-definitions-v3 count [--filter-json @filter.json]`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 create --ticket-definition-json @ticket-definition.json`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 update --ticket-definition-id <ticket_definition_id> --ticket-definition-json @ticket-definition.json`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 reorder --request-json @reorder.json`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 delete --ticket-definition-id <ticket_definition_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-definitions-v3 delete --ticket-definition-id <ticket_definition_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 bulk-delete-by-filter --filter-json @filter.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-definitions-v3 bulk-delete-by-filter --filter-json @filter.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-definitions-v3 change-currency --request-json @currency.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-definitions-v3 change-currency --request-json @currency.json [--receipt-out receipt.json]`

Notes for Events Ticket Definitions V3:
- `get`, `query`, and `count` are reads/helpers for ticket definition records.
- `create`, `update`, and `reorder` are reviewed-plan writes.
- `update` requires the current `ticketDefinition.revision`.
- `delete`, `bulk-delete-by-filter`, and `change-currency` also require `--ack-irreversible`.
- Official Wix docs say the Wix Events & Tickets app must be installed, ticket definitions are not tickets, and Orders API generates tickets after purchase.
- Official Wix docs say callable methods require `Manage Ticket Definitions`, and `create` allows up to 100 definitions per event.
- This family remains live-unverified.

## Manage Wix Events Categories

- `wix-safe-agent-cli events-categories get --category-id <category_id>`
- `wix-safe-agent-cli events-categories query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json events-categories create --category-json @category.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories bulk-create --categories-json @categories.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories update --category-id <category_id> --category-json @category.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories assign-events --category-id <category_id> --events-json @events.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories bulk-assign-events --request-json @assign.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories reorder-events --category-id <category_id> --request-json @reorder.json`
- `wix-safe-agent-cli --plan-out plan.json events-categories delete --category-id <category_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-categories delete --category-id <category_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-categories unassign-events --category-id <category_id> --event-ids <event_id,event_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-categories unassign-events --category-id <category_id> --event-ids <event_id,event_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-categories bulk-unassign-events --category-ids <category_id,category_id> --event-ids <event_id,event_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-categories bulk-unassign-events --category-ids <category_id,category_id> --event-ids <event_id,event_id> [--receipt-out receipt.json]`

Notes for Events Categories:
- `get` and `query` are reads/helpers for event categories.
- `create`, `bulk-create`, `update`, `assign-events`, `bulk-assign-events`, and `reorder-events` are reviewed-plan writes.
- `delete`, `unassign-events`, and `bulk-unassign-events` also require `--ack-irreversible`.
- Official Wix docs say the Wix Events & Tickets app must be installed and category methods require `Manage Events`.
- This family remains live-unverified.

## Manage Wix Events Schedule Items

- `wix-safe-agent-cli events-schedule-items get --item-id <item_id>`
- `wix-safe-agent-cli events-schedule-items list [--params-json @params.json]`
- `wix-safe-agent-cli events-schedule-items query [--query-json @query.json]`
- `wix-safe-agent-cli events-schedule-items list-bookmarks [--params-json @params.json]`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items add --schedule-item-json @schedule-item.json`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items update --item-id <item_id> --schedule-item-json @schedule-item.json`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items publish-draft --request-json @publish.json`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items reschedule-draft --request-json @reschedule.json`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items create-bookmark --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items delete-bookmark --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items delete --request-json @delete.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-schedule-items delete --request-json @delete.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-schedule-items discard-draft --request-json @discard.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-schedule-items discard-draft --request-json @discard.json [--receipt-out receipt.json]`

Notes for Events Schedule Items:
- `get`, `list`, `query`, and `list-bookmarks` are reads/helpers for event schedule items and current-member bookmarks.
- `add`, `update`, `publish-draft`, `reschedule-draft`, `create-bookmark`, and `delete-bookmark` are reviewed-plan writes.
- `delete` and `discard-draft` also require `--ack-irreversible`.
- Official Wix docs say each event has one published schedule and one draft schedule; draft changes are not public until published.
- Official Wix docs say Wix Events & Tickets must be installed and schedule item methods require `Manage Events`.
- This family remains live-unverified.

## Manage Wix Events Policies V2

- `wix-safe-agent-cli events-policies-v2 get --policy-id <policy_id>`
- `wix-safe-agent-cli events-policies-v2 query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json events-policies-v2 create --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json events-policies-v2 update --policy-id <policy_id> --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json events-policies-v2 reorder --request-json @reorder.json`
- `wix-safe-agent-cli --plan-out plan.json events-policies-v2 delete --policy-id <policy_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-policies-v2 delete --policy-id <policy_id> [--receipt-out receipt.json]`

Notes for Events Policies V2:
- `get` and `query` are reads/helpers for event policy records.
- `create`, `update`, and `reorder` are reviewed-plan writes.
- `delete` permanently deletes a policy and also requires `--ack-irreversible`.
- Official Wix docs say Wix Events & Tickets must be installed, an event can have up to 3 policies, reads use `Read Policies`, writes use `Manage Policies`, and update requires the current policy `revision`.
- Reorder changes how policies appear in the event dashboard and agreement checkbox on the RSVP or checkout form.
- This family remains live-unverified.

## Manage Wix Events Staff Members

- `wix-safe-agent-cli events-staff-members get --staff-member-id <staff_member_id>`
- `wix-safe-agent-cli events-staff-members query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json events-staff-members create --staff-member-json @staff-member.json`
- `wix-safe-agent-cli --plan-out plan.json events-staff-members update --staff-member-id <staff_member_id> --staff-member-json @staff-member.json`
- `wix-safe-agent-cli --plan-out plan.json events-staff-members delete --staff-member-id <staff_member_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-staff-members delete --staff-member-id <staff_member_id> [--receipt-out receipt.json]`

Notes for Events Staff Members:
- `get` and `query` are reads/helpers for event staff member records.
- `create` and `update` are reviewed-plan writes.
- `update` requires the current `staffMember.revision`.
- `delete` permanently removes a staff member from the staff member list and also requires `--ack-irreversible`.
- Official Wix docs say Wix Events & Tickets must be installed and methods require `Manage Events - all permissions`.
- Query defaults to `createdDate ASC` with paging limit `100` and offset `0`.
- This family remains live-unverified.

## Query Wix Events Guests

- `wix-safe-agent-cli events-guests query [--query-json @query.json]`

Notes for Events Guests:
- `query` is a read/helper command for event guest records, including RSVP guests and ticket buyers.
- Official Wix docs say Wix Events & Tickets must be installed.
- Guest details are returned only when the request includes the `guestDetails` fieldset.
- Query Event Guests can be called as a Wix app or Wix user identity and requires `Read Event Tickets and Guest List`.
- Query defaults to `createdDate ASC` with paging limit `100` and offset `0`.
- Event Guest created/deleted/updated and attendance events are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Events RSVPs V2

- `wix-safe-agent-cli events-rsvps-v2 get --rsvp-id <rsvp_id>`
- `wix-safe-agent-cli events-rsvps-v2 query [--query-json @query.json]`
- `wix-safe-agent-cli events-rsvps-v2 search --search-json @search.json`
- `wix-safe-agent-cli events-rsvps-v2 count [--count-json @count.json]`
- `wix-safe-agent-cli events-rsvps-v2 list-summary --event-id <event_id> [--event-id <event_id>]`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 create --rsvp-json @rsvp.json`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 update --rsvp-id <rsvp_id> --rsvp-json @rsvp.json`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 bulk-update --rsvps-json @rsvps.json`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 check-in --rsvp-id <rsvp_id> [--request-json @check-in.json]`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 delete --rsvp-id <rsvp_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-rsvps-v2 delete --rsvp-id <rsvp_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 bulk-delete-by-filter --filter-json @filter.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-rsvps-v2 bulk-delete-by-filter --filter-json @filter.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-rsvps-v2 cancel-check-in --rsvp-id <rsvp_id> [--request-json @cancel.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-rsvps-v2 cancel-check-in --rsvp-id <rsvp_id> [--request-json @cancel.json] [--receipt-out receipt.json]`

Notes for Events RSVPs V2:
- `get`, `query`, `search`, `count`, and `list-summary` are reads/helpers for RSVP records and RSVP summary counts.
- `create`, `update`, `bulk-update`, and `check-in` are reviewed-plan writes.
- `delete`, `bulk-delete-by-filter`, and `cancel-check-in` are reviewed-plan writes that also require `--ack-irreversible` because they remove RSVP records or check-in evidence.
- Official Wix docs say Wix Events & Tickets must be installed. Read commands require `Read Event Tickets and Guest List`; create requires `Manage Events`; update, delete, bulk actions, check-in, and cancel check-in require `Manage Guest List`.
- `update` requires the current `rsvp.revision`, and `bulk-update` requires a revision for each RSVP and accepts up to `100` RSVPs.
- `check-in` and `cancel-check-in` can process up to `11` guests in one request.
- Query defaults to `createdDate ASC` with paging limit `100` and offset `0`.
- RSVP created/updated/deleted pages are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Events Ticket Reservations

- `wix-safe-agent-cli events-ticket-reservations get --ticket-reservation-id <ticket_reservation_id>`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-reservations create --reservation-json @reservation.json`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-reservations bulk-update-tags --tags-json @tags.json`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-reservations delete --ticket-reservation-id <ticket_reservation_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-reservations delete --ticket-reservation-id <ticket_reservation_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-reservations bulk-update-tags-by-filter --filter-json @filter.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-reservations bulk-update-tags-by-filter --filter-json @filter.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-ticket-reservations cancel --ticket-reservation-id <ticket_reservation_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-ticket-reservations cancel --ticket-reservation-id <ticket_reservation_id> [--receipt-out receipt.json]`

Notes for Events Ticket Reservations:
- `get` is a read/helper for one ticket reservation.
- `create` and `bulk-update-tags` are reviewed-plan writes.
- `delete`, `bulk-update-tags-by-filter`, and `cancel` are reviewed-plan writes that also require `--ack-irreversible` because delete cannot be undone, by-filter tag updates can affect all reservations when the filter is empty, and canceled reservations cannot be restored.
- Official Wix docs say Wix Events & Tickets must be installed. Create, get, and cancel require `Events Checkout`; delete and bulk tag updates require `Manage Orders`.
- `create` starts a `PENDING` ticket reservation that auto-expires if not confirmed. `ticketReservation.tickets` must include 1-50 line items.
- `bulk-update-tags` uses an `ids` array and supports up to `100` ticket reservations.
- Ticket Reservation created/deleted/updated pages are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Events Tickets

- `wix-safe-agent-cli events-tickets get --ticket-number <ticket_number>`
- `wix-safe-agent-cli events-tickets list [--params-json @params.json]`
- `wix-safe-agent-cli --plan-out plan.json events-tickets update --ticket-number <ticket_number> --ticket-json @ticket.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-tickets update --ticket-number <ticket_number> --ticket-json @ticket.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-tickets bulk-update --tickets-json @tickets.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-tickets bulk-update --tickets-json @tickets.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-tickets check-in --request-json @check-in.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-tickets check-in --request-json @check-in.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-tickets delete-check-in --request-json @delete-check-in.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-tickets delete-check-in --request-json @delete-check-in.json [--receipt-out receipt.json]`

Notes for Events Tickets:
- `get` and `list` are reads/helpers for purchased event tickets.
- `update`, `bulk-update`, and `check-in` are reviewed-plan writes.
- `delete-check-in` is a reviewed-plan write that also requires `--ack-irreversible` because it removes attendance check-in evidence.
- Official Wix docs say Wix Events & Tickets must be installed and tickets are generated by the Orders API.
- `get` and `list` require `Read Event Tickets and Guest List`; write methods require `Manage Guest List`.
- `list` retrieves up to `100` tickets with the specified paging, filtering, and sorting.
- `bulk-update`, `check-in`, and `delete-check-in` accept up to `100` ticket numbers through the official `ticketNumber` array.
- Order Updated is a webhook/event surface, not a CLI command.
- This family remains live-unverified.

## Read and manage Wix Events Orders and checkout

- `wix-safe-agent-cli events-orders list [--params-json @params.json]`
- `wix-safe-agent-cli events-orders get --event-id <event_id> --order-number <order_number>`
- `wix-safe-agent-cli --plan-out plan.json events-orders update --event-id <event_id> --order-number <order_number> --order-json @order.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-orders update --event-id <event_id> --order-number <order_number> --order-json @order.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders bulk-update --event-id <event_id> --orders-json @orders.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-orders bulk-update --event-id <event_id> --orders-json @orders.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders confirm --event-id <event_id> --request-json @confirm.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-orders confirm --event-id <event_id> --request-json @confirm.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli events-orders get-summary [--params-json @params.json]`
- `wix-safe-agent-cli events-orders get-checkout-options [--params-json @params.json]`
- `wix-safe-agent-cli events-orders list-available-tickets [--params-json @params.json]`
- `wix-safe-agent-cli events-orders query-available-tickets [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders create-reservation --reservation-json @reservation.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-orders create-reservation --reservation-json @reservation.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders cancel-reservation --reservation-id <reservation_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-orders cancel-reservation --reservation-id <reservation_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders checkout --checkout-json @checkout.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-orders checkout --checkout-json @checkout.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-orders update-checkout --order-number <order_number> --checkout-json @checkout.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-orders update-checkout --order-number <order_number> --checkout-json @checkout.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli events-orders get-invoice --reservation-id <reservation_id> [--invoice-json @invoice.json]`

Notes for Events Orders and checkout:
- `list`, `get`, `get-summary`, `get-checkout-options`, `list-available-tickets`, `query-available-tickets`, and `get-invoice` are reads/helpers.
- `update`, `bulk-update`, and `update-checkout` are reviewed-plan writes.
- `confirm`, `create-reservation`, `cancel-reservation`, and `checkout` also require `--ack-irreversible` because they can change paid order status, create contacts/orders, send confirmation email, or hold/release ticket inventory.
- Official Wix docs say Wix Events & Tickets must be installed. Paid ticket checkout also requires a premium plan and at least one configured payment method.
- Order reads require `Read Basic Events Order Info`; order writes require `Manage Orders`; checkout methods require `Events Checkout`.
- `query-available-tickets` enforces the official `limit` maximum of `1000` and `offset` minimum of `0`.
- The old checkout `create-reservation` and `cancel-reservation` endpoints are deprecated; use the newer `events-ticket-reservations` commands when possible.
- Order deleted/updated/confirmed/initiated/paid and deprecated reservation created/updated pages are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Events registration forms

- `wix-safe-agent-cli events-forms get-form --event-id <event_id>`
- `wix-safe-agent-cli --plan-out plan.json events-forms discard-draft --event-id <event_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-forms discard-draft --event-id <event_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-forms add-control --event-id <event_id> --control-json @control.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-forms add-control --event-id <event_id> --control-json @control.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-forms update-control --event-id <event_id> --control-id <control_id> --control-json @control.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json events-forms update-control --event-id <event_id> --control-id <control_id> --control-json @control.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-forms delete-control --event-id <event_id> --control-id <control_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-forms delete-control --event-id <event_id> --control-id <control_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-forms update-messages --event-id <event_id> --messages-json @messages.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-forms update-messages --event-id <event_id> --messages-json @messages.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json events-forms publish-draft --event-id <event_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json events-forms publish-draft --event-id <event_id> [--receipt-out receipt.json]`

Notes for Events registration forms:
- `get-form` is a read/helper for one event registration form.
- `add-control` and `update-control` are reviewed-plan writes.
- `discard-draft`, `delete-control`, `update-messages`, and `publish-draft` also require `--ack-irreversible` because they clear draft changes, remove form fields, change visitor-facing registration copy, or publish draft form changes.
- Official Wix docs say Wix Events & Tickets must be installed. `get-form` requires `Read Events`; write methods require `Manage Events` and Wix app or Wix user identity.
- Name and email controls are always required and pinned to the top of the form.
- Add, update, and delete control changes can automatically trigger form publishing.
- `discard-draft` and `publish-draft` are deprecated. Wix says publish returns the existing form after deprecation and discard returns an empty object after deprecation.
- Form Event Updated is a webhook/event surface, not a CLI command.
- This family remains live-unverified.

## Read and manage Wix Restaurants menus

Use these commands to inspect restaurant menu records and keep menu changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-menus list [--params-json '{"onlyVisible":true}']`
- `wix-safe-agent-cli restaurants-menus get --menu-id <menu_id>`
- `wix-safe-agent-cli restaurants-menus query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus create --menu-json @menu.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus update --menu-id <menu_id> --menu-json @menu.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus delete --menu-id <menu_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus bulk-create --menus-json @menus.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus bulk-update --menus-json @menus.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus duplicate --menu-id <menu_id> [--options-json '{"menuName":"Dinner Copy"}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-menus update-extended-fields --menu-id <menu_id> --extended-fields-json @extended-fields.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-menus create --menu-json @menu.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-menus delete --menu-id <menu_id> [--receipt-out receipt.json]`

Notes for Restaurants Menus:
- `restaurants-menus list`, `get`, and `query` are reads/helpers.
- `restaurants-menus create`, `update`, `bulk-create`, `bulk-update`, `duplicate`, and `update-extended-fields` are reviewed-plan writes.
- `restaurants-menus delete` also requires `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Menus family is Developer Preview.
- Writes use `Manage Restaurants - all permissions`; update and bulk update require the current menu revision.
- List/query can return up to `500` menus.
- The official markdown schema currently lists `/restaurants/menus/v1` paths while rendered examples/page data show the public `/restaurants/menus-menu/v1` paths used by this CLI.
- Menu Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified. Other Restaurants subfamilies remain open.

## Read and manage Wix Restaurants menu sections

Use these commands to inspect restaurant menu sections and keep section changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-sections list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-sections get --section-id <section_id>`
- `wix-safe-agent-cli restaurants-sections query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections create --section-json @section.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections update --section-id <section_id> --section-json @section.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections delete --section-id <section_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections bulk-create --sections-json @sections.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections bulk-delete --sections-json @sections.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections bulk-update --sections-json @sections.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-sections duplicate --section-id <section_id> [--options-json '{"businessLocationIds":["loc_1"]}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-sections create --section-json @section.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-sections delete --section-id <section_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-sections bulk-delete --sections-json @sections.json [--receipt-out receipt.json]`

Notes for Restaurants Sections:
- `restaurants-sections list`, `get`, and `query` are reads/helpers.
- `restaurants-sections create`, `update`, `bulk-create`, `bulk-update`, and `duplicate` are reviewed-plan writes.
- `restaurants-sections delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Sections family is Developer Preview.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require the current section revision.
- List/query can return up to `500` sections.
- Wix warns that adding the same section to multiple menus can break some site functionality, so section reuse should be reviewed before applying duplicate or relationship-changing payloads.
- The official markdown schema currently lists `/restaurants/menus/v1` paths while rendered examples/page data show the public `/restaurants/menus-section/v1` paths used by this CLI.
- Section Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified. Other Restaurants subfamilies remain open.

## Read and manage Wix Restaurants menu items

Use these commands to inspect restaurant menu items and keep item changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-items list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-items get --item-id <item_id>`
- `wix-safe-agent-cli restaurants-items query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-items search [--search-json '{"search":{"expression":"salad"}}']`
- `wix-safe-agent-cli restaurants-items count [--filter-json '{"filter":{"visible":true}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items create --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items update --item-id <item_id> --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items delete --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items bulk-create --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items bulk-delete --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-items bulk-update --items-json @items.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-items create --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-items delete --item-id <item_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-items bulk-delete --items-json @items.json [--receipt-out receipt.json]`

Notes for Restaurants Items:
- `restaurants-items list`, `get`, `query`, `search`, and `count` are reads/helpers.
- `restaurants-items create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `restaurants-items delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require the current item revision.
- List returns up to `500` items. Search defaults to `paging.limit` `500`, `paging.offset` `0`, and `createdDate` ascending. Count can count all items when no filter is sent. Bulk update handles up to `100` items.
- Current rendered method pages do not show a stable method-level Developer Preview marker for this Items slice.
- The official markdown schema currently lists `/restaurants/menus/v1` paths while rendered examples/page data show the public `/restaurants/menus-item/v1` paths used by this CLI.
- Item Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified. Other Restaurants subfamilies remain open.

## Read and manage Wix Restaurants item labels

Use these commands to inspect restaurant item labels and keep label changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-item-labels list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-item-labels get --label-id <label_id>`
- `wix-safe-agent-cli restaurants-item-labels query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-labels create --label-json @label.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-labels update --label-id <label_id> --label-json @label.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-labels delete --label-id <label_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-item-labels create --label-json @label.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-labels delete --label-id <label_id> [--receipt-out receipt.json]`

Notes for Restaurants Item Labels:
- `restaurants-item-labels list`, `get`, and `query` are reads/helpers.
- `restaurants-item-labels create` and `update` are reviewed-plan writes.
- `restaurants-item-labels delete` also requires `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Item Labels family is Developer Preview.
- Create/update/delete use `Manage Restaurants - all permissions`; current rendered get/list/query pages show `Wix Multilingual - Nile Wrapper Domain Events Read`.
- Update requires the current label revision. List/query can return up to `500` labels.
- Item Label Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified. Other Restaurants subfamilies remain open.

## Read and manage Wix Restaurants item variants

Use these commands to inspect restaurant item variants and keep variant changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-item-variants list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-item-variants get --variant-id <variant_id>`
- `wix-safe-agent-cli restaurants-item-variants query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-item-variants count [--filter-json '{"filter":{"name":"Large"}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants create --variant-json @variant.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants update --variant-id <variant_id> --variant-json @variant.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants delete --variant-id <variant_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants bulk-create --variants-json @variants.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants bulk-delete --variants-json @variants.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-variants bulk-update --variants-json @variants.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-item-variants create --variant-json @variant.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-variants delete --variant-id <variant_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-variants bulk-delete --variants-json @variants.json [--receipt-out receipt.json]`

Notes for Restaurants Item Variants:
- `restaurants-item-variants list`, `get`, `query`, and `count` are reads/helpers.
- `restaurants-item-variants create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `restaurants-item-variants delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Item Variants family is Developer Preview.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require the current variant revision.
- List/query can return up to `500` variants. Count can count all variants when no filter is sent. Bulk update returns up to `100` item variants.
- Item Variant Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants item modifiers

Use these commands to inspect restaurant item modifiers and keep modifier changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-item-modifiers list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-item-modifiers get --modifier-id <modifier_id>`
- `wix-safe-agent-cli restaurants-item-modifiers query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-item-modifiers count [--filter-json '{"filter":{"name":"Almond milk"}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers create --modifier-json @modifier.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers update --modifier-id <modifier_id> --modifier-json @modifier.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers delete --modifier-id <modifier_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers bulk-create --modifiers-json @modifiers.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers bulk-delete --modifiers-json @modifiers.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifiers bulk-update --modifiers-json @modifiers.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-item-modifiers create --modifier-json @modifier.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-modifiers delete --modifier-id <modifier_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-modifiers bulk-delete --modifiers-json @modifiers.json [--receipt-out receipt.json]`

Notes for Restaurants Item Modifiers:
- `restaurants-item-modifiers list`, `get`, `query`, and `count` are reads/helpers.
- `restaurants-item-modifiers create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `restaurants-item-modifiers delete` and `bulk-delete` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Item Modifiers family is Developer Preview.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require the current modifier revision.
- List/query can return up to `500` modifiers. Count can count all modifiers when no filter is sent.
- Item Modifier Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants item modifier groups

Use these commands to inspect restaurant item modifier groups and keep modifier-group changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-item-modifier-groups list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-item-modifier-groups get --modifier-group-id <modifier_group_id>`
- `wix-safe-agent-cli restaurants-item-modifier-groups query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-item-modifier-groups count [--filter-json '{"filter":{"name":"Pizza toppings"}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifier-groups create --modifier-group-json @modifier-group.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifier-groups update --modifier-group-id <modifier_group_id> --modifier-group-json @modifier-group.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifier-groups delete --modifier-group-id <modifier_group_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifier-groups bulk-create --modifier-groups-json @modifier-groups.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-item-modifier-groups bulk-update --modifier-groups-json @modifier-groups.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-item-modifier-groups create --modifier-group-json @modifier-group.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-item-modifier-groups delete --modifier-group-id <modifier_group_id> [--receipt-out receipt.json]`

Notes for Restaurants Item Modifier Groups:
- `restaurants-item-modifier-groups list`, `get`, `query`, and `count` are reads/helpers.
- `restaurants-item-modifier-groups create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `restaurants-item-modifier-groups delete` also requires `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Menus app must be installed.
- The Item Modifier Groups family is Developer Preview.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require the current modifier group revision.
- List/query can return up to `500` modifier groups. Count can count all modifier groups when no filter is sent. Bulk create accepts up to `100` modifier groups, and bulk update can return up to `100` modifier groups.
- The official bulk update page renders the endpoint as `/restaurants/item-modifier-group/v1/bulk/modifiers-groups/update`.
- Item Modifier Group Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders operation groups

Use these commands to inspect online order operation groups and keep operation-group changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-operation-groups get --operation-group-id <operation_group_id>`
- `wix-safe-agent-cli restaurants-online-order-operation-groups query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups create --operation-group-json @operation-group.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups update --operation-group-id <operation_group_id> --operation-group-json @operation-group.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups delete --operation-group-id <operation_group_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups bulk-create --operation-groups-json @operation-groups.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups bulk-delete --operation-groups-json @operation-groups.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups bulk-update --operation-groups-json @operation-groups.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups bulk-update-tags --tags-json @operation-group-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operation-groups bulk-update-tags-by-filter --filter-json @operation-group-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-operation-groups create --operation-group-json @operation-group.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-operation-groups delete --operation-group-id <operation_group_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-operation-groups bulk-update-tags-by-filter --filter-json @operation-group-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Operation Groups:
- `restaurants-online-order-operation-groups get` and `query` are reads/helpers.
- `restaurants-online-order-operation-groups create`, `update`, `bulk-create`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-operation-groups delete`, `bulk-delete`, and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require current operation group revisions.
- Deleting an operation group deletes the operations that belong to it.
- `bulk-update-tags-by-filter` is async and can update all operation groups when no filter is specified.
- Operation Group Created, Updated, and Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders operations

Use these commands to inspect online order operations, calculate availability, and keep operation changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-operations get --operation-id <operation_id>`
- `wix-safe-agent-cli restaurants-online-order-operations list [--params-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli restaurants-online-order-operations query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-online-order-operations first-available-time-slot-per-fulfillment-type --operation-id <operation_id> [--params-json @params.json]`
- `wix-safe-agent-cli restaurants-online-order-operations first-available-time-slots-per-operation --operations-json @operations.json`
- `wix-safe-agent-cli restaurants-online-order-operations first-available-time-slots-per-menu --operation-id <operation_id> [--params-json @params.json]`
- `wix-safe-agent-cli restaurants-online-order-operations available-time-slots-for-date --operation-id <operation_id> [--params-json @params.json]`
- `wix-safe-agent-cli restaurants-online-order-operations available-dates-in-range --operation-id <operation_id> [--params-json @params.json]`
- `wix-safe-agent-cli restaurants-online-order-operations validate-address --operation-id <operation_id> [--params-json @params.json]`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operations update --operation-id <operation_id> --operation-json @operation.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operations delete --operation-id <operation_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operations bulk-update-tags --tags-json @operation-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-operations bulk-update-tags-by-filter --filter-json @operation-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-operations update --operation-id <operation_id> --operation-json @operation.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-operations delete --operation-id <operation_id> [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Operations:
- `restaurants-online-order-operations get`, `list`, `query`, availability calculations, and `validate-address` are reads/helpers.
- `restaurants-online-order-operations update` and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-operations delete` and `bulk-update-tags-by-filter` also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed.
- The current rendered pages show Developer Preview and use `/restaurants-operations/v1` public paths.
- Methods use `Manage Restaurants - all permissions`; update requires the current operation revision.
- Operations are automatically created from operation groups and locations.
- `bulk-update-tags-by-filter` is async and can update all operations when no filter is specified.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders menu ordering settings

Use these commands to inspect menu ordering settings and keep menu availability changes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-menu-ordering-settings get --menu-ordering-settings-id <menu_ordering_settings_id>`
- `wix-safe-agent-cli restaurants-online-order-menu-ordering-settings query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-online-order-menu-ordering-settings list-menus-availability-status`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings update --menu-ordering-settings-id <menu_ordering_settings_id> --menu-ordering-settings-json @menu-ordering-settings.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings bulk-update --menu-ordering-settings-json @menu-ordering-settings.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings bulk-update-tags --tags-json @menu-ordering-settings-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter --filter-json @menu-ordering-settings-tag-filter.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings update-extended-fields --menu-ordering-settings-id <menu_ordering_settings_id> --extended-fields-json @extended-fields.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-menu-ordering-settings upsert-by-menu-id --menu-id <menu_id> --upsert-json @menu-ordering-settings.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-menu-ordering-settings update --menu-ordering-settings-id <menu_ordering_settings_id> --menu-ordering-settings-json @menu-ordering-settings.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter --filter-json @menu-ordering-settings-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Menu Ordering Settings:
- `restaurants-online-order-menu-ordering-settings get`, `query`, and `list-menus-availability-status` are reads/helpers.
- `restaurants-online-order-menu-ordering-settings update`, `bulk-update`, `bulk-update-tags`, `update-extended-fields`, and `upsert-by-menu-id` are reviewed-plan writes.
- `restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter` is a reviewed-plan write that also requires `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app and Wix Restaurants Menus app must be installed.
- The current rendered pages show Developer Preview and use `/menu-ordering-settings/v1` public paths.
- Methods use `Manage Restaurants - all permissions`; update and bulk update require current revisions.
- Menu ordering settings are created automatically for each menu.
- `bulk-update-tags-by-filter` is async and can update all menu ordering settings when no filter is specified.
- Menu Ordering Settings Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders fulfillment methods

Use these commands to inspect fulfillment methods, check availability helpers, and keep fulfillment-method writes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods list [--params-json '{"paging.limit":50}']`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods get --fulfillment-method-id <fulfillment_method_id>`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods list-available-for-address --address-json @address.json`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-accumulated-availability [--params-json '{}']`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-combined-availability [--params-json '{}']`
- `wix-safe-agent-cli restaurants-online-order-fulfillment-methods get-aggregated-availability --availability-json @availability.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods create --fulfillment-method-json @fulfillment-method.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods bulk-create --fulfillment-methods-json @fulfillment-methods.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods update --fulfillment-method-id <fulfillment_method_id> --fulfillment-method-json @fulfillment-method.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods delete --fulfillment-method-id <fulfillment_method_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods bulk-update-tags --tags-json @fulfillment-method-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter --filter-json @fulfillment-method-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-fulfillment-methods update --fulfillment-method-id <fulfillment_method_id> --fulfillment-method-json @fulfillment-method.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-fulfillment-methods delete --fulfillment-method-id <fulfillment_method_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter --filter-json @fulfillment-method-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Fulfillment Methods:
- `restaurants-online-order-fulfillment-methods list`, `get`, `query`, `list-available-for-address`, `get-accumulated-availability`, `get-combined-availability`, and `get-aggregated-availability` are reads/helpers.
- `restaurants-online-order-fulfillment-methods create`, `bulk-create`, and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-fulfillment-methods update` is a reviewed-plan write and requires `fulfillmentMethod.revision`.
- `restaurants-online-order-fulfillment-methods delete` and `bulk-update-tags-by-filter` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed.
- The current rendered pages show Developer Preview and use `/fulfillment-methods/v1` public paths.
- Methods use `Manage Restaurants - all permissions`.
- Get Accumulated Fulfillment Methods Availability and Get Combined Method Availability are deprecated by Wix; Get Aggregated Method Availability is the replacement named in the docs.
- Fulfillment Method Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders availability exceptions

Use these commands to inspect and manage availability exceptions while keeping writes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-availability-exceptions get --availability-exception-id <availability_exception_id>`
- `wix-safe-agent-cli restaurants-online-order-availability-exceptions query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions create --availability-exception-json @availability-exception.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions bulk-create --availability-exceptions-json @availability-exceptions.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions update --availability-exception-id <availability_exception_id> --availability-exception-json @availability-exception.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions bulk-update --availability-exceptions-json @availability-exceptions.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions delete --availability-exception-id <availability_exception_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions bulk-update-tags --tags-json @availability-exception-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-availability-exceptions bulk-update-tags-by-filter --filter-json @availability-exception-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-availability-exceptions update --availability-exception-id <availability_exception_id> --availability-exception-json @availability-exception.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-availability-exceptions delete --availability-exception-id <availability_exception_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-availability-exceptions bulk-update-tags-by-filter --filter-json @availability-exception-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Availability Exceptions:
- `restaurants-online-order-availability-exceptions get` and `query` are reads/helpers.
- `restaurants-online-order-availability-exceptions create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-availability-exceptions update` and `bulk-update` require current revisions.
- `restaurants-online-order-availability-exceptions delete` and `bulk-update-tags-by-filter` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed and each availability exception requires a restaurant operation ID.
- The current rendered pages show Developer Preview and use `/restaurants-availability-exceptions/v1` public paths.
- Methods use `Manage Restaurants - all permissions`.
- Availability Exception Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders service fee rules

Use these commands to calculate fees, inspect service fee rules, and keep rule writes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-service-fees calculate --order-json @order.json`
- `wix-safe-agent-cli restaurants-online-order-service-fees list [--params-json '{"locationId":"<location_id>"}']`
- `wix-safe-agent-cli restaurants-online-order-service-fees get --rule-id <rule_id>`
- `wix-safe-agent-cli restaurants-online-order-service-fees query [--query-json '{"query":{"cursorPaging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees create --rule-json @rule.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees bulk-create --rules-json @rules.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees update --rule-id <rule_id> --rule-json @rule.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees bulk-update --rules-json @rules.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees delete --rule-id <rule_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees bulk-delete --rules-json @rule-ids.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees bulk-update-tags --tags-json @rule-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-service-fees bulk-update-tags-by-filter --filter-json @rule-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-service-fees update --rule-id <rule_id> --rule-json @rule.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-service-fees delete --rule-id <rule_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-service-fees bulk-delete --rules-json @rule-ids.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-service-fees bulk-update-tags-by-filter --filter-json @rule-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Service Fees:
- `restaurants-online-order-service-fees calculate`, `list`, `get`, and `query` are reads/helpers.
- `restaurants-online-order-service-fees create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-service-fees update` and `bulk-update` require current rule revisions.
- `restaurants-online-order-service-fees delete`, `bulk-delete`, and `bulk-update-tags-by-filter` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed.
- The current rendered pages show Developer Preview and use `/service-fees/v1` public paths.
- Methods use `Manage Restaurants - all permissions`.
- `bulk-update-tags-by-filter` is async and can update all rules when no filter is specified.
- Rule Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Online Orders notification recipients

Use these commands to inspect and manage notification recipients while keeping recipient writes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-online-order-notification-recipients get --recipient-id <recipient_id>`
- `wix-safe-agent-cli restaurants-online-order-notification-recipients query [--query-json '{"query":{"cursorPaging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients create --recipient-json @recipient.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients bulk-create --recipients-json @recipients.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients update --recipient-id <recipient_id> --recipient-json @recipient.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients bulk-update --recipients-json @recipients.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients delete --recipient-id <recipient_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients bulk-delete --recipients-json @recipient-ids.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients bulk-update-tags --tags-json @recipient-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-online-order-notification-recipients bulk-update-tags-by-filter --filter-json @recipient-tag-filter.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-online-order-notification-recipients update --recipient-id <recipient_id> --recipient-json @recipient.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-notification-recipients delete --recipient-id <recipient_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-notification-recipients bulk-delete --recipients-json @recipient-ids.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-online-order-notification-recipients bulk-update-tags-by-filter --filter-json @recipient-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Online Orders Notification Recipients:
- `restaurants-online-order-notification-recipients get` and `query` are reads/helpers.
- `restaurants-online-order-notification-recipients create`, `bulk-create`, `update`, `bulk-update`, and `bulk-update-tags` are reviewed-plan writes.
- `restaurants-online-order-notification-recipients update` and `bulk-update` require current recipient revisions.
- `restaurants-online-order-notification-recipients delete`, `bulk-delete`, and `bulk-update-tags-by-filter` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Restaurants Orders app must be installed.
- The current rendered pages show Developer Preview and use `/rest-notification-recipients/v1` public paths.
- Methods use `Manage Restaurants - all permissions`.
- `bulk-update-tags-by-filter` can affect a broad recipient set.
- Recipient Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Restaurants Reservations

Use these commands to inspect and manage restaurant reservations while keeping lifecycle writes inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-reservations get --reservation-id <reservation_id> [--params-json '{"fieldsets":["FULL"]}']`
- `wix-safe-agent-cli restaurants-reservations list [--params-json '{"limit":50}']`
- `wix-safe-agent-cli restaurants-reservations query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-reservations search [--search-json '{"search":{"expression":"Ada"}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations create --reservation-json @reservation.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations update --reservation-id <reservation_id> --reservation-json @reservation.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations delete --reservation-id <reservation_id>`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations bulk-archive --reservations-json @reservation-ids.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations bulk-unarchive --reservations-json @reservation-ids.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations cancel --reservation-id <reservation_id> [--request-json @cancel.json]`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations create-held --reservation-json @held-reservation.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservations reserve --reservation-id <reservation_id> [--request-json @reserve.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-reservations update --reservation-id <reservation_id> --reservation-json @reservation.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-reservations delete --reservation-id <reservation_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-reservations cancel --reservation-id <reservation_id> [--request-json @cancel.json] [--receipt-out receipt.json]`

Notes for Restaurants Reservations:
- `restaurants-reservations get`, `list`, `query`, and `search` are reads/helpers.
- `restaurants-reservations create`, `update`, `bulk-archive`, `bulk-unarchive`, `create-held`, and `reserve` are reviewed-plan writes.
- `restaurants-reservations update` requires the current reservation revision.
- `restaurants-reservations delete` and `cancel` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Table Reservations app must be installed and at least 1 location must be configured in the Dashboard under Business Info.
- The current rendered pages show Developer Preview and use `/table-reservations/reservations/v1` public paths.
- `get` with the `FULL` fieldset requires stronger reservation permissions.
- `create-held` creates a `HELD` reservation that expires after 10 minutes.
- `reserve` changes a `HELD` reservation to `RESERVED` or `REQUESTED`, depending on manual approval settings.
- `delete` only deletes reservations with `HELD` status.
- Archived reservations are hidden from the dashboard's normal reservations view and cannot be updated until unarchived.
- Reservation Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read and update Wix Restaurants Reservation Locations

Use these commands to inspect reservation-location configuration and keep updates inside the reviewed-plan flow.

- `wix-safe-agent-cli restaurants-reservation-locations get --reservation-location-id <reservation_location_id> [--params-json '{"fieldsets":["FULL"]}']`
- `wix-safe-agent-cli restaurants-reservation-locations list [--params-json '{"limit":50}']`
- `wix-safe-agent-cli restaurants-reservation-locations query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservation-locations update --reservation-location-id <reservation_location_id> --reservation-location-json @reservation-location.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-reservation-locations update --reservation-location-id <reservation_location_id> --reservation-location-json @reservation-location.json [--receipt-out receipt.json]`

Notes for Restaurants Reservation Locations:
- `restaurants-reservation-locations get`, `list`, and `query` are reads/helpers.
- `restaurants-reservation-locations update` is a reviewed-plan write.
- `restaurants-reservation-locations update` requires the current `reservationLocation.revision`.
- Official Wix docs say the Wix Table Reservations app must be installed.
- The current rendered pages show Developer Preview and use `/table-reservations/reservation-locations/v1` public paths.
- Reservation locations can only be created and archived through the Dashboard or Locations API.
- Reservation Location Created and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read Wix Restaurants Reservation Time Slots

Use these commands to check restaurant reservation availability and retrieve scheduled or nearby time slots.

- `wix-safe-agent-cli restaurants-reservation-time-slots check --time-slot-json @time-slot-check.json`
- `wix-safe-agent-cli restaurants-reservation-time-slots get-scheduled --time-slots-json @scheduled-time-slots.json`
- `wix-safe-agent-cli restaurants-reservation-time-slots get --time-slots-json @time-slots.json`

Notes for Restaurants Reservation Time Slots:
- `restaurants-reservation-time-slots check`, `get-scheduled`, and `get` are reads/helpers.
- Official Wix docs say the Wix Table Reservations app must be installed and at least 1 location must be configured in the Dashboard under Business Info.
- The current rendered pages show Developer Preview and use `/table-reservations/reservations/v1` public paths.
- `check` checks whether a reservation location can seat a given party size in a specific time slot.
- `get-scheduled` returns scheduled time slots within the reservation location's `businessSchedule`; an experience ID can be passed in the request body when checking an experience with its own schedule.
- `get` returns the time slot at the specified date and can use `slotsBefore` and `slotsAfter` in the request body to retrieve nearby time slots.
- Time slot statuses include `AVAILABLE`, `UNAVAILABLE`, and `NON_WORKING_HOURS`, and responses can indicate whether manual approval is required.
- This family remains live-unverified.

## Read and manage Wix Restaurants Experiences

Use these commands to inspect and manage reservation experiences while keeping writes inside the reviewed-plan flow.

- `wix-safe-agent-cli --plan-out plan.json restaurants-reservation-experiences create --experience-json @experience.json`
- `wix-safe-agent-cli restaurants-reservation-experiences get --experience-id <experience_id> [--params-json '{"fieldsets":["FULL"]}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservation-experiences update --experience-id <experience_id> --experience-json @experience.json`
- `wix-safe-agent-cli restaurants-reservation-experiences query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli restaurants-reservation-experiences search [--search-json '{"search":{"expression":"chef"}}']`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservation-experiences bulk-update-tags --tags-json @experience-tags.json`
- `wix-safe-agent-cli --plan-out plan.json restaurants-reservation-experiences bulk-update-tags-by-filter --filter-json @experience-tag-filter.json`
- `wix-safe-agent-cli restaurants-reservation-experiences get-by-slug --slug <slug> [--params-json '{"fieldsets":["FULL"]}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json restaurants-reservation-experiences update --experience-id <experience_id> --experience-json @experience.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json restaurants-reservation-experiences bulk-update-tags-by-filter --filter-json @experience-tag-filter.json [--receipt-out receipt.json]`

Notes for Restaurants Experiences:
- `restaurants-reservation-experiences get`, `query`, `search`, and `get-by-slug` are reads/helpers.
- `create`, `update`, and `bulk-update-tags` are reviewed-plan writes.
- `bulk-update-tags-by-filter` is a reviewed-plan write that also requires `--ack-irreversible` because broad filters can retag many experiences.
- Official Wix docs say the Wix Table Reservations app must be installed and at least 1 reservation location must be configured.
- The current rendered pages show Developer Preview and use `/table-reservations/experiences/v1` public paths.
- `update` requires the current `experience.revision`.
- Experience Created, Tags Modified, and Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Read Wix Blog Posts and Stats

Use these commands to inspect published blog posts and their post metrics.

- `wix-safe-agent-cli blog-posts-stats get --post-id <post_id> [--params-json '{}']`
- `wix-safe-agent-cli blog-posts-stats query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli blog-posts-stats list [--params-json '{"paging.limit":50}']`
- `wix-safe-agent-cli blog-posts-stats get-by-slug --slug <slug> [--params-json '{}']`
- `wix-safe-agent-cli blog-posts-stats get-metrics --post-id <post_id> [--params-json '{}']`
- `wix-safe-agent-cli blog-posts-stats get-total [--params-json '{}']`
- `wix-safe-agent-cli blog-posts-stats query-count [--params-json '{"rangeStart":"2026-01-01","months":3}']`

Notes for Blog Posts and Stats:
- All `blog-posts-stats` commands are reads/helpers.
- Official Wix docs say these methods use `Read Blog`.
- `query` and `list` retrieve up to `100` posts per request.
- `query` and `list` default to `firstPublishedDate` descending with pinned posts first, `paging.limit` `50`, and `paging.offset` `0`.
- `query-count` returns monthly published-post counts for a `rangeStart` and number of `months`; empty months are omitted from the response.
- Post Created, Deleted, Liked, Unliked, and Updated are webhook/event surfaces, not CLI commands.
- Blog Likes is shipped as an explicit command family; only the Like Created and Like Deleted event pages are marked Developer Preview.
- This family remains live-unverified.

## Manage Wix Blog Draft Posts

Use these commands to inspect drafts, prepare draft changes, publish drafts, and manage trashed drafts.

- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts create --draft-post-json @draft-post.json`
- `wix-safe-agent-cli blog-draft-posts get --draft-post-id <draft_post_id> [--params-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts update --draft-post-id <draft_post_id> --draft-post-json @draft-post.json`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts delete --draft-post-id <draft_post_id>`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts delete --draft-post-id <draft_post_id> --permanent`
- `wix-safe-agent-cli blog-draft-posts query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli blog-draft-posts list [--params-json '{"paging.limit":50}']`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts bulk-create --draft-posts-json @draft-posts.json`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts bulk-delete --draft-posts-json @draft-posts-delete.json`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts bulk-update --draft-posts-json @draft-posts.json`
- `wix-safe-agent-cli blog-draft-posts get-deleted --draft-post-id <draft_post_id> [--params-json '{}']`
- `wix-safe-agent-cli blog-draft-posts list-deleted [--params-json '{"paging.limit":50}']`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts publish --draft-post-id <draft_post_id> [--publish-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts remove-from-trash-bin --draft-post-id <draft_post_id>`
- `wix-safe-agent-cli --plan-out plan.json blog-draft-posts restore-from-trash-bin --draft-post-id <draft_post_id> [--restore-json '{}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json blog-draft-posts update --draft-post-id <draft_post_id> --draft-post-json @draft-post.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json blog-draft-posts remove-from-trash-bin --draft-post-id <draft_post_id> [--receipt-out receipt.json]`

Notes for Blog Draft Posts:
- `get`, `query`, `list`, `get-deleted`, and `list-deleted` are reads/helpers.
- `create`, `update`, `delete`, `bulk-create`, `bulk-update`, `publish`, and `restore-from-trash-bin` are reviewed-plan writes.
- `delete --permanent`, `bulk-delete`, and `remove-from-trash-bin` also require `--ack-irreversible`.
- Official Wix docs say these methods require Wix app or Wix user authentication and `Manage Blog`.
- A single draft post has a 400KB size limit.
- For third-party apps, Create Draft Post requires `memberId`.
- Unknown category IDs in create requests are silently omitted by Wix.
- `query` and `list` retrieve up to `100` draft posts per request and default to `editedDate DESC`, `paging.limit` `50`, and `paging.offset` `0`.
- `delete` normally moves a draft to the trash bin. `delete --permanent` and `remove-from-trash-bin` cannot be restored.
- `publish` creates a new published post from the draft, or updates the published post when the draft was already published.
- Draft Deleted, Draft Post Created, and Draft Post Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Blog Categories

Use these commands to inspect and manage Wix Blog categories.

- `wix-safe-agent-cli --plan-out plan.json blog-categories create --category-json @category.json`
- `wix-safe-agent-cli blog-categories get --category-id <category_id> [--params-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json blog-categories update --category-id <category_id> --category-json @category.json`
- `wix-safe-agent-cli --plan-out plan.json blog-categories delete --category-id <category_id>`
- `wix-safe-agent-cli blog-categories query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli blog-categories list [--params-json '{"paging.limit":50}']`
- `wix-safe-agent-cli blog-categories get-by-slug --slug <slug> [--params-json '{}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json blog-categories update --category-id <category_id> --category-json @category.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json blog-categories delete --category-id <category_id> [--receipt-out receipt.json]`

Notes for Blog Categories:
- `get`, `query`, `list`, and `get-by-slug` are reads/helpers.
- `create` and `update` are reviewed-plan writes.
- `delete` is a reviewed-plan write that also requires `--ack-irreversible` because category removal changes blog navigation.
- Official Wix docs say create/update/delete require Wix app or Wix user authentication and `Manage Blog`; reads require `Read Blog`.
- Sites can have up to `100` categories per language and up to `10` categories per post.
- `query` and `list` default to `paging.limit` `50` and `paging.offset` `0`; `list` sorts by `displayPosition DESC` and cannot be overridden.
- Category Created, Category Deleted, and Category Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Blog Tags

Use these commands to inspect and manage Wix Blog tags.

- `wix-safe-agent-cli blog-tags get --tag-id <tag_id> [--params-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json blog-tags delete --tag-id <tag_id>`
- `wix-safe-agent-cli blog-tags query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json blog-tags create --tag-json @tag.json`
- `wix-safe-agent-cli blog-tags get-by-label --label <label> [--params-json '{}']`
- `wix-safe-agent-cli blog-tags get-by-slug --slug <slug> [--params-json '{}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json blog-tags create --tag-json @tag.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json blog-tags delete --tag-id <tag_id> [--receipt-out receipt.json]`

Notes for Blog Tags:
- `get`, `query`, `get-by-label`, and `get-by-slug` are reads/helpers.
- `create` is a reviewed-plan write.
- `delete` is a reviewed-plan write that also requires `--ack-irreversible` because Wix removes that tag from every blog post that contains it.
- Official Wix docs say create/delete require Wix app or Wix user authentication and `Manage Blog`; reads require `Read Blog`.
- A post can have up to `30` tags. The introduction says each tag is limited to `50` characters, while the tag object page shows `label` and `slug` max lengths of `100`.
- `query` returns up to `500` tags and defaults to `postCount DESC`, `paging.limit` `50`, and `paging.offset` `0`.
- `get-by-label` supports labels containing `/`; Wix treats the whole path after `labels/` as one label.
- Tag Created, Tag Deleted, and Tag Updated are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Manage Wix Blog Likes

Use these commands to inspect and manage Wix Blog likes for the current visitor or member.

- `wix-safe-agent-cli --plan-out plan.json blog-likes create --like-json @like.json`
- `wix-safe-agent-cli blog-likes get --like-id <like_id> [--params-json '{}']`
- `wix-safe-agent-cli --plan-out plan.json blog-likes delete --like-id <like_id>`
- `wix-safe-agent-cli blog-likes query [--query-json '{"query":{"paging":{"limit":50}}}']`
- `wix-safe-agent-cli --plan-out plan.json blog-likes delete-by-fqdn-entity-id --fqdn wix.blog.v3.post --entity-id <entity_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json blog-likes create --like-json @like.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json blog-likes delete --like-id <like_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json blog-likes delete-by-fqdn-entity-id --fqdn wix.blog.v3.post --entity-id <entity_id> [--receipt-out receipt.json]`

Notes for Blog Likes:
- The callable `blog-likes` methods are not marked Developer Preview in the current Wix docs; the Like Created and Like Deleted event pages are Developer Preview.
- `get` and `query` are reads/helpers for likes created by the current authenticated visitor or member through the API.
- `create` is a reviewed-plan write.
- `delete` and `delete-by-fqdn-entity-id` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Blog app must be installed.
- Official Wix docs say these methods require visitor or member authentication. Create/delete methods use `Manage Blog`; get/query use `Read Blog`.
- `get` and `query` do not return Blog UI likes, likes from other visitors, or a complete list of all likes for a piece of content.
- `query` returns up to `100` likes and defaults to `createdDate DESC`, `paging.limit` `50`, and `paging.offset` `0`.
- Like Created and Like Deleted are webhook/event surfaces, not CLI commands.
- This family remains live-unverified.

## Disabled Wix Forum

There are no `forum-*` commands.

Notes for Wix Forum:
- Official Wix docs still list historical Forum category and post methods, including category/post get, get-by-slug, and query methods.
- Wix says Forum APIs were deprecated on October 15, 2025 and Wix Forum was discontinued on March 1, 2026.
- Wix says forum data was deleted after the discontinuation date, so this CLI does not expose runnable Forum commands.
- The old Forum methods and events are accounted in `docs/official_inventory.json` as disabled/non-callable.
- Wix docs direct migration work to Groups API.

## Manage custom embeds

Use these commands to inspect or manage custom HTML/JavaScript embeds on the current site context.

- `wix-safe-agent-cli custom-embeds list [--limit N] [--offset N]`
- `wix-safe-agent-cli custom-embeds get --custom-embed-id <id>`
- `wix-safe-agent-cli --plan-out plan.json custom-embeds create --custom-embed-json '{"name":"Header","position":"HEAD","embedData":{"category":"ESSENTIAL","html":"<script></script>"}}'`
- `wix-safe-agent-cli --plan-out plan.json custom-embeds update --custom-embed-id <id> --custom-embed-json '{"revision":"1","name":"Updated Header"}'`
- `wix-safe-agent-cli --plan-out plan.json custom-embeds delete --custom-embed-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json custom-embeds create --custom-embed-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json custom-embeds update --custom-embed-id <id> --custom-embed-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json custom-embeds delete --custom-embed-id <id> [--receipt-out receipt.json]`

Notes for Custom Embeds:
- `custom-embeds list` is read-only and returns up to 100 custom embeds sorted by position.
- `custom-embeds get` is read-only for one custom embed ID.
- `custom-embeds create`, `custom-embeds update`, and `custom-embeds delete` are reviewed-plan writes.
- `custom-embeds update` requires the current revision number because Wix documents revision-based conflict protection.
- `custom-embeds delete` requires `--ack-irreversible`.
- The family intro and write pages say Wix app or Wix user identity auth, while the get/list pages prominently show permission and endpoint details but may omit the auth paragraph. This tool keeps that docs inconsistency explicit and remains live-unverified.
- Custom embed HTML/JS is live site code, not ordinary data. Verification is reread-based and recovery is manual only.

## Manage site secrets

Use these commands to inspect secret metadata, fetch one secret value, or carefully create, patch, and delete secrets for the current site context.

- `wix-safe-agent-cli secrets list`
- `wix-safe-agent-cli secrets get-value --name <secret_name>`
- `wix-safe-agent-cli --plan-out plan.json secrets create --secret-json '{"name":"API_KEY","value":"<secret>","description":"Primary key"}'`
- `wix-safe-agent-cli --plan-out plan.json secrets patch --secret-id <id> --secret-json '{"description":"Updated description"}'`
- `wix-safe-agent-cli --plan-out plan.json secrets delete --secret-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json secrets create --secret-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json secrets patch --secret-id <id> --secret-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json secrets delete --secret-id <id> [--receipt-out receipt.json]`

Notes for Secrets:
- `secrets list` is read-only and returns secret metadata only, never secret values.
- `secrets get-value` is read-only but returns the actual secret value, so use it only in backend-safe workflows.
- `secrets create`, `secrets patch`, and `secrets delete` are reviewed-plan writes.
- `secrets delete` requires `--ack-irreversible`.
- Plans and receipts never store secret values. They keep metadata only.
- Wix docs say the Members Area app must be installed before a site can create or manage secrets, but it is not required for `secrets get-value`.
- Wix docs also say deleting a secret, or changing its name or value, breaks code that uses that secret.

## Manage sender email setup

Use these commands to set up verified email addresses, sender identities, and authenticated sending domains for Wix email flows.

- `wix-safe-agent-cli sender-emails list [--email-address <email>] [--limit N] [--cursor <cursor>]`
- `wix-safe-agent-cli sender-emails get --sender-email-id <id>`
- `wix-safe-agent-cli --plan-out plan.json sender-emails create --sender-email-json '{"senderEmail":{"emailAddress":"owner@example.com"}}'`
- `wix-safe-agent-cli --plan-out plan.json sender-emails delete --sender-email-id <id>`
- `wix-safe-agent-cli --plan-out plan.json sender-emails get-or-create --email-address owner@example.com`
- `wix-safe-agent-cli --plan-out plan.json sender-emails send-verification-code --sender-email-id <id>`
- `wix-safe-agent-cli --plan-out plan.json sender-emails verify --sender-email-id <id> --verification-code ABC123`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-emails create --sender-email-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json sender-emails delete --sender-email-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-emails get-or-create --email-address owner@example.com [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-emails send-verification-code --sender-email-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-emails verify --sender-email-id <id> --verification-code ABC123 [--receipt-out receipt.json]`
- `wix-safe-agent-cli sender-details list [--limit N] [--cursor <cursor>]`
- `wix-safe-agent-cli sender-details get --sender-details-id <id>`
- `wix-safe-agent-cli sender-details get-default`
- `wix-safe-agent-cli --plan-out plan.json sender-details create --sender-details-json '{"senderDetails":{"fromName":"Owner","fromEmailAddress":"owner@example.com"}}'`
- `wix-safe-agent-cli --plan-out plan.json sender-details update --sender-details-id <id> --sender-details-json '{"senderDetails":{"fromName":"New Owner"}}'`
- `wix-safe-agent-cli --plan-out plan.json sender-details delete --sender-details-id <id>`
- `wix-safe-agent-cli --plan-out plan.json sender-details mark-default --sender-details-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-details create --sender-details-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-details update --sender-details-id <id> --sender-details-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json sender-details delete --sender-details-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sender-details mark-default --sender-details-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli sending-domains get --sending-domain-id <id>`
- `wix-safe-agent-cli sending-domains query --domain example.com`
- `wix-safe-agent-cli sending-domains query --sending-domain-id <id>`
- `wix-safe-agent-cli sending-domains query --query-json '{"query":{"filter":{"domain":"example.com"}}}'`
- `wix-safe-agent-cli --plan-out plan.json sending-domains authenticate --sending-domain-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json sending-domains authenticate --sending-domain-id <id> [--receipt-out receipt.json]`

Notes for Sender setup:
- `sender-emails list` and `sender-emails get` are read-only in this boundary.
- `sender-emails create`, `delete`, `get-or-create`, `send-verification-code`, and `verify` are reviewed-plan writes.
- `sender-emails delete` requires `--ack-irreversible`.
- `sender-emails send-verification-code` uses provider-response-only verification because inbox delivery happens outside this CLI.
- `sender-emails verify` proves success by rereading the sender email and checking `verified: true`.
- `sender-details list`, `get`, and `get-default` are reads. `create`, `update`, `delete`, and `mark-default` are reviewed-plan writes.
- `sender-details delete` requires `--ack-irreversible`.
- Wix docs say you can only create sender details for a verified email address.
- `sending-domains query` requires a filter by `domain` or `id`, matching the official Wix docs.
- `sending-domains authenticate` is a reviewed-plan write and this CLI refuses it unless the current status is `NOT_AUTHENTICATED`.
- Wix docs say DNS propagation can take up to 48 hours, so sending-domain authentication remains live-unverified even after local contract tests pass.

## Read and manage marketing consent

Use these commands to inspect newsletter or SMS opt-in state, create confirmed consent safely, and revoke consent with a reviewed plan.

- `wix-safe-agent-cli marketing-consent get --marketing-consent-id <marketing_consent_id>`
- `wix-safe-agent-cli marketing-consent query --query-json '{"query":{"filter":{"state":{"$eq":"CONFIRMED"}},"cursorPaging":{"limit":10}}}'`
- `wix-safe-agent-cli marketing-consent get-by-identifier --type EMAIL --email owner@example.com [--link-language en]`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent create --marketing-consent-json '{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"FORM","optInLevel":"SINGLE_CONFIRMATION"}}'`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent update --marketing-consent-json '{"id":"<marketing_consent_id>","details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"FORM","optInLevel":"SINGLE_CONFIRMATION"}}' --mask-json '{"paths":["state","lastConfirmationActivity.source","lastConfirmationActivity.optInLevel"]}'`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent delete --marketing-consent-id <marketing_consent_id> --ack-irreversible`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent upsert --marketing-consent-json '{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"PENDING","lastConfirmationActivity":{"source":"FORM","optInLevel":"DOUBLE_CONFIRMATION"}}'`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent bulk-upsert --marketing-consents-json '{"info":[{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"FORM","optInLevel":"SINGLE_CONFIRMATION"}}]}'`
- `wix-safe-agent-cli --plan-out plan.json marketing-consent remove --type EMAIL --email owner@example.com --last-revoke-activity-json '{"source":"REVOKE_LINK"}'`

Notes for Marketing consent:
- `marketing-consent get`, `query`, and `get-by-identifier` are reads.
- `marketing-consent create`, `update`, `upsert`, `bulk-upsert`, and `remove` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `marketing-consent delete` is an irreversible reviewed-plan delete that also requires `--ack-irreversible`.
- `marketing-consent query` returns up to 100 items per request and defaults to sort `id ASC`.
- `marketing-consent create` is limited here to confirmed single-confirmation consent and refuses existing identifiers so the caller must switch to `upsert`.
- `marketing-consent update` requires `--mask-json` plus a payload `id`; for existing email consent records, Wix keeps the current state if the caller tries to patch it to `UNKNOWN_STATE`.
- `marketing-consent upsert` is the path for double-confirmation or other state changes.
- `marketing-consent bulk-upsert` accepts either a raw JSON array or an object with `info`, and the CLI enforces the official `500`-item limit before send.
- `marketing-consent remove` changes the state to `REVOKED` but does not delete the entity.
- The official `get-by-identifier` page currently renders the query parameters badly in the portal, so this CLI follows the official example path with `type` plus `email` or `phone`.
- The official `remove` page says `lastRevokeActivity` is required even though the curl example omits it, so this CLI stays strict and requires `--last-revoke-activity-json`.

## Read and manage referral program settings

Use these commands to inspect the site referral program, activate or pause it, generate AI social post suggestions, or update settings with the current revision.

- `wix-safe-agent-cli referral-program get`
- `wix-safe-agent-cli referral-program get-premium-features`
- `wix-safe-agent-cli referral-program get-ai-social-media-posts-suggestions`
- `wix-safe-agent-cli --plan-out plan.json referral-program activate`
- `wix-safe-agent-cli --plan-out plan.json referral-program pause`
- `wix-safe-agent-cli --plan-out plan.json referral-program generate-ai-social-media-posts-suggestions`
- `wix-safe-agent-cli --plan-out plan.json referral-program update --program-json '{"program":{"revision":"<current_revision>"}}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referral-program activate [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referral-program pause [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referral-program generate-ai-social-media-posts-suggestions [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referral-program update --program-json @program.json [--receipt-out receipt.json]`

Notes for Referral Program:
- `referral-program get`, `get-premium-features`, and `get-ai-social-media-posts-suggestions` are reads.
- `referral-program activate`, `pause`, `generate-ai-social-media-posts-suggestions`, and `update` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- Wix docs say the Referral Program API requires a qualifying Wix site plan, at least one supported Wix business app, and only one referral program per site.
- `referral-program update` requires the current program revision in `--program-json`.
- `referral-program generate-ai-social-media-posts-suggestions` creates a new suggestion set; use `get-ai-social-media-posts-suggestions` to inspect existing suggestions.
- Program Updated stays callback-only.

## Read referral rewards

Use these commands to inspect reward records created by a site's referral program.

- `wix-safe-agent-cli referral-rewards get --referral-reward-id <referral_reward_id>`
- `wix-safe-agent-cli referral-rewards query --query-json '{"query":{"filter":{"rewardType":{"$eq":"COUPON"}},"sort":[{"fieldName":"createdDate","order":"DESC"}],"cursorPaging":{"limit":10}}}'`

Notes for Referral Rewards:
- `referral-rewards get` and `query` are read/helper commands.
- Wix docs say Referral Rewards requires a qualifying Wix site plan and at least one supported Wix business app.
- Both methods use Wix app or Wix user identity auth and `Manage Referrals`.
- Query supports official filters and sorting for `rewardedReferringCustomerId`, `rewardedReferredFriendId`, `rewardType`, `createdDate`, and `updatedDate`.

## Read referring customers

Use these commands to inspect referring customer records created by a site's referral program.

- `wix-safe-agent-cli referring-customers get --referring-customer-id <referring_customer_id>`
- `wix-safe-agent-cli referring-customers query --query-json '{"query":{"filter":{"contactId":{"$eq":"<contact_id>"}},"sort":[{"fieldName":"createdDate","order":"DESC"}],"cursorPaging":{"limit":10}}}'`
- `wix-safe-agent-cli referring-customers get-by-referral-code --referral-code GxpxwAoMqxH8`
- `wix-safe-agent-cli --plan-out plan.json referring-customers generate-for-contact --contact-id <contact_id_or_me>`
- `wix-safe-agent-cli --plan-out plan.json referring-customers delete --referring-customer-id <referring_customer_id> --revision <current_revision>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referring-customers generate-for-contact --contact-id <contact_id_or_me> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json referring-customers delete --referring-customer-id <referring_customer_id> --revision <current_revision> [--receipt-out receipt.json]`

Notes for Referring Customers:
- `referring-customers get`, `query`, and `get-by-referral-code` are read/helper commands.
- `referring-customers generate-for-contact` is a reviewed-plan write using a `contactId` body. Wix docs say `"me"` can be used instead of a specific contact ID.
- `referring-customers delete` is an irreversible reviewed-plan delete that requires `--ack-irreversible` and sends the current `revision` as a REST query parameter.
- Wix docs say Referring Customers requires a qualifying Wix site plan and at least one supported Wix business app.
- The implemented methods use Wix app or Wix user identity auth and `Manage Referrals`.
- Query supports official filters and sorting for `contactId`, `referralCode`, `createdDate`, and `updatedDate`.
- Referring Customer Created and Deleted stay callback-only.

## Read and manage referred friends

Use these commands to inspect or safely manage referred friend records created by a site's referral program.

- `wix-safe-agent-cli referred-friends get --referred-friend-id <referred_friend_id>`
- `wix-safe-agent-cli referred-friends query --query-json '{"query":{"filter":{"status":{"$eq":"ACTIONS_COMPLETED"}},"sort":[{"fieldName":"updatedDate","order":"DESC"}],"cursorPaging":{"limit":10}}}'`
- `wix-safe-agent-cli referred-friends get-by-contact-id --contact-id <contact_id_or_me>`
- `wix-safe-agent-cli --plan-out plan.json referred-friends create --referral-code 9zb9JvjwrvQF`
- `wix-safe-agent-cli --plan-out plan.json referred-friends update --referred-friend-json '{"referredFriend":{"id":"<referred_friend_id>","contactId":"<contact_id>","referringCustomerId":"<referring_customer_id>","status":"ACTIONS_COMPLETED","revision":"<current_revision>"}}'`
- `wix-safe-agent-cli --plan-out plan.json referred-friends delete --referred-friend-id <referred_friend_id> --revision <current_revision>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referred-friends create --referral-code 9zb9JvjwrvQF [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json referred-friends update --referred-friend-json '{"referredFriend":{"id":"<referred_friend_id>","contactId":"<contact_id>","referringCustomerId":"<referring_customer_id>","status":"ACTIONS_COMPLETED","revision":"<current_revision>"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json referred-friends delete --referred-friend-id <referred_friend_id> --revision <current_revision> [--receipt-out receipt.json]`

Notes for Referred Friends:
- `referred-friends get`, `query`, and `get-by-contact-id` are read/helper commands. Wix docs say `me` can be used with `get-by-contact-id` for the current identity's contact.
- `referred-friends create` is a reviewed-plan write using a 12-character `referralCode`. Wix docs say the call must use member identity and may return an existing entity if it already exists.
- `referred-friends update` is a reviewed-plan write using the official `referredFriend` request object with `id`, `contactId`, `referringCustomerId`, and current `revision`.
- `referred-friends delete` is an irreversible reviewed-plan delete that requires `--ack-irreversible` and sends the current `revision` as a REST query parameter.
- Wix docs say Referred Friends requires a qualifying Wix site plan and at least one supported Wix business app.
- The implemented methods use Wix app or Wix user identity auth and `Manage Referrals`, except create also requires member identity.
- Query supports official filters and sorting for `referringCustomerId`, `status`, `createdDate`, and `updatedDate`.
- Referred Friend Created, Updated, and Deleted stay callback-only.

## Read referral tracker events

Use these commands to inspect referral events and statistics for a site's referral program.

- `wix-safe-agent-cli referral-tracker get --referral-event-id <referral_event_id>`
- `wix-safe-agent-cli referral-tracker query --query-json '{"query":{"filter":{"createdDate":{"$exists":true}},"sort":[{"fieldName":"createdDate","order":"DESC"}],"cursorPaging":{"limit":10}}}'`
- `wix-safe-agent-cli referral-tracker get-statistics`

Notes for Referral Tracker:
- `referral-tracker get`, `query`, and `get-statistics` are read/helper commands.
- Wix docs say Referral Tracker requires the Wix Loyalty Program app, a qualifying Wix site plan, and at least one supported Wix business app.
- The implemented methods use Wix app or Wix user identity auth and `Manage Referrals`.
- Query supports official filters and sorting for `referredFriendSignupEvent`, `successfulReferralEvent`, `actionEvent`, `rewardEvent`, `createdDate`, and `updatedDate`; the separate filter-and-sort page also lists `eventType`, `createdDate`, and `updatedDate`.
- Referral Event Created stays callback-only.

## Read and manage email campaign state

Use these commands to inspect existing Wix email campaigns, publish one, reuse a copy, delete one, pause a scheduled send, reschedule a send, or send a test before any wider campaign workflow is opened in this tool.

- `wix-safe-agent-cli email-campaigns list [--include-statistics] [--statuses-json '["ACTIVE"]'] [--visibility-statuses-json '["DRAFT"]'] [--limit N] [--offset N]`
- `wix-safe-agent-cli email-campaigns get --campaign-id <id> [--include-statistics]`
- `wix-safe-agent-cli email-campaigns get-audience --campaign-id <id>`
- `wix-safe-agent-cli email-campaigns list-statistics --campaign-ids-json '["<campaign_id>"]'`
- `wix-safe-agent-cli email-campaigns list-recipients --campaign-id <id> --activity OPENED [--limit N] [--cursor <cursor>]`
- `wix-safe-agent-cli email-campaigns identify-sender-address --email-address owner@example.com`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns pause-scheduling --campaign-id <id>`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns reschedule --campaign-id <id> --send-at <rfc3339-send-time>`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns send-test --campaign-id <id> --send-test-json @send-test.json`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns publish --campaign-id <id> [--publish-json @publish.json]`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns reuse --campaign-id <id>`
- `wix-safe-agent-cli --plan-out plan.json email-campaigns delete --campaign-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-campaigns pause-scheduling --campaign-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-campaigns reschedule --campaign-id <id> --send-at <rfc3339-send-time> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-campaigns send-test --campaign-id <id> --send-test-json @send-test.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-campaigns publish --campaign-id <id> [--publish-json @publish.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-campaigns reuse --campaign-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json email-campaigns delete --campaign-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli campaign-validation validate-link --url https://example.com`
- `wix-safe-agent-cli campaign-validation validate-html-links --html '<a href="https://example.com">Example</a>'`

Notes for Email campaigns:
- `list`, `get`, `get-audience`, `list-statistics`, `list-recipients`, and `identify-sender-address` are read/helper calls in the current command surface.
- `pause-scheduling`, `reschedule`, `send-test`, `publish`, `reuse`, and `delete` are reviewed-plan writes. Use `--plan-out` first, then `--plan-in --apply --yes` for live apply.
- `pause-scheduling` rereads the campaign and expects `distributionStatus=PAUSED`.
- `reschedule` is provider-response-only because the current read surface does not prove the scheduled time directly.
- `send-test` is rate-limited in the official docs and is provider-response-only here because inbox delivery happens outside this CLI.
- `publish` may publish landing-page-only when no `emailDistributionOptions` body is supplied, verifies by provider response plus readback of the published campaign, and requires `sendAt` to be at least 30 minutes ahead when scheduling a send.
- `reuse` creates a new campaign copy and verifies by the returned `campaignId` plus readback when possible.
- `delete` is permanent, requires `--ack-irreversible`, and verifies by expecting `get` to return 404 after apply.
- Official Wix docs say campaigns must already exist in Wix before API access. This API does not create a brand-new campaign from scratch.
- Official Wix docs say the Campaign API works only when the site's email-marketing account is `ACTIVE` and quota has not been reached.
- `email-campaigns list-statistics` supports up to 100 campaign IDs in one request.
- `email-campaigns list-recipients` requires one activity filter and supports `DELIVERED`, `OPENED`, `CLICKED`, `BOUNCED`, `NOT_SENT`, `SENT`, and `NOT_OPENED`.
- `campaign-validation validate-link` and `campaign-validation validate-html-links` help check link safety and abuse-rule compliance before any send flow is opened.
- Campaign lifecycle writes now shipped in the current subset: `pause-scheduling`, `reschedule`, `send-test`, `publish`, `reuse`, and `delete`.

## Read and manage pricing plans

Use these commands to inspect Pricing Plans V3 inventory, count or search plans, and make plan-first changes to one plan or up to 100 plans in one reviewed request.

- `wix-safe-agent-cli pricing-plans get --plan-id <plan_id>`
- `wix-safe-agent-cli pricing-plans query [--query-json '{"filter":{"archived":{"$eq":false}}}']`
- `wix-safe-agent-cli pricing-plans search [--search-json '{"search":{"expression":"gold"}}']`
- `wix-safe-agent-cli pricing-plans count [--filter-json '{"archived":{"$eq":false}}']`
- `wix-safe-agent-cli --plan-out plan.json pricing-plans create --pricing-plan-json @pricing-plan.json`
- `wix-safe-agent-cli --plan-out plan.json pricing-plans update --plan-id <plan_id> --pricing-plan-json @pricing-plan.json`
- `wix-safe-agent-cli --plan-out plan.json pricing-plans delete --plan-id <plan_id>`
- `wix-safe-agent-cli --plan-out plan.json pricing-plans bulk-update --bulk-update-json @pricing-plans-bulk-update.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pricing-plans create --pricing-plan-json @pricing-plan.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pricing-plans update --plan-id <plan_id> --pricing-plan-json @pricing-plan.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json pricing-plans delete --plan-id <plan_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pricing-plans bulk-update --bulk-update-json @pricing-plans-bulk-update.json [--receipt-out receipt.json]`

Notes for Pricing Plans:
- `pricing-plans get`, `query`, `search`, and `count` are reads.
- `pricing-plans create`, `update`, and `bulk-update` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `pricing-plans delete` is an irreversible reviewed-plan delete and also requires `--ack-irreversible`.
- Official Wix docs say reads use `Read Orders` and `Read Pricing Plans`, while writes use `Manage Pricing Plans`.
- `pricing-plans query` defaults to `createdDate ASC` with `cursorPaging.limit 100` unless the request overrides it.
- `pricing-plans search` can include aggregations when the official request body asks for them.
- The official update page currently renders the path placeholder as `{plan.id}`. This CLI still uses `--plan-id` as the explicit selector and rereads the same plan ID after apply.
- `pricing-plans bulk-update` accepts either a raw plans array or a full official body object, normalizes request items into the official `plans[].plan` shape, defaults `returnEntity` to `true` when omitted, rejects duplicate target plan IDs, and refuses plan-name changes because official Wix docs say bulk update can't rename plans.

## Read and manage Stores Catalog V3 products

Use these commands to inspect and manage Catalog V3 products, including bulk changes, inventory-coupled product writes, category helpers, info-section helpers, and variant filter helpers.

- `wix-safe-agent-cli stores-products-v3 get --product-id <product_id>`
- `wix-safe-agent-cli stores-products-v3 get-by-slug --slug <product_slug>`
- `wix-safe-agent-cli stores-products-v3 get-all-products-category`
- `wix-safe-agent-cli stores-products-v3 query [--query-json '{"filter":{"visible":{"$eq":true}}}']`
- `wix-safe-agent-cli stores-products-v3 search [--search-json '{"search":{"expression":"shirt"}}']`
- `wix-safe-agent-cli stores-products-v3 count [--filter-json '{"visible":{"$eq":true}}']`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 create --product-json @product.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 update --product-id <product_id> --product-json @product.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 delete --product-id <product_id>`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-create --products-json @products.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-delete --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-update --products-json @products.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 create-with-inventory --product-json @product.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 update-with-inventory --product-id <product_id> --product-json @product.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-create-with-inventory --products-json @products.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-update-with-inventory --products-json @products.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-add-info-sections --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-add-info-sections-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-add-to-categories-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-adjust-variants-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-delete-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-remove-info-sections --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-remove-info-sections-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-remove-from-categories-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-update-variants-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json stores-products-v3 bulk-update-by-filter --request-json @request.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-products-v3 create --product-json @product.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-products-v3 update --product-id <product_id> --product-json @product.json [--receipt-out receipt.json]`

Notes for Stores Products V3:
- `stores-products-v3 get`, `get-by-slug`, `get-all-products-category`, `query`, `search`, and `count` are reads/helpers.
- All product writes are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `delete`, `bulk-delete`, `bulk-delete-by-filter`, remove-info-section commands, and `bulk-remove-from-categories-by-filter` also require `--ack-irreversible`.
- The shipped Stores Products V3 boundary is Catalog V3-only.
- Official Wix docs say reads use `Read v3 catalog`, non-visible products may also need `Product v3 read admin`, normal product writes use `Product write in v3 catalog`, and inventory-coupled writes also use `Inventory write in v3 catalog`.
- `stores-products-v3 update`, `bulk-update`, `update-with-inventory`, and `bulk-update-with-inventory` require the current product `revision`.
- `stores-products-v3 query` and `search` return up to `100` products and do not include full variant detail, so use `get`, `get-by-slug`, or `read-only-variants-v3` when you need variant-level detail.
- This family is locally proven and still live-unverified.

## Query and search Stores Catalog V3 variants directly

Use these commands to work with Catalog V3 variants as primary entities when product-level reads do not give enough detail.

- `wix-safe-agent-cli read-only-variants-v3 query [--query-json '{"filter":{"productData.productId":{"$eq":"product-1"},"variantId":{"$eq":"variant-1"}}}']`
- `wix-safe-agent-cli read-only-variants-v3 search [--search-json '{"search":{"expression":"red shirt"}}']`

Notes for Read-Only Variants V3:
- `read-only-variants-v3 query` and `search` are read-only commands.
- Official Wix docs say the Wix Stores app must be installed.
- Reads use `Read products in v3 catalog`, and non-visible variants may also need `Product v3 read admin`.
- `read-only-variants-v3 query` should use `productData.productId` together with `variantId` as the unique variant key because `id` is deprecated and not globally unique by itself.
- Both methods support up to `1,000` variants per request.
- `read-only-variants-v3 search` defaults to `productData.updatedDate DESC`, then `productData.productId ASC`, then `variantId ASC` when no explicit sort is supplied.
- Official Wix docs also say this family is eventually consistent with Products V3 writes, so verify critical real-time changes against Products V3 when needed.
- This family is locally proven and still live-unverified.

## Read Stores Catalog V3 brands

Use these commands to inspect existing Catalog V3 brands before you decide whether to add the broader brand write and bulk flows.

- `wix-safe-agent-cli brands-v3 get --brand-id <brand_id>`
- `wix-safe-agent-cli brands-v3 query [--query-json '{"filter":{"name":{"$startsWith":"Ac"}}}']`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 create --brand-json '{"name":"Acme"}'`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 update --brand-id <brand_id> --brand-json '{"name":"Acme","revision":"1"}'`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 delete --brand-id <brand_id>`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 bulk-create --brands-json '[{"name":"Acme"}]'`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 bulk-delete --brand-ids-json '["<brand_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 bulk-update --brands-json '[{"id":"<brand_id>","name":"Acme","revision":"1"}]'`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 get-or-create --brand-name Acme`
- `wix-safe-agent-cli --plan-out plan.json brands-v3 bulk-get-or-create --brand-names-json '["Acme"]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json brands-v3 create --brand-json '{"name":"Acme"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json brands-v3 delete --brand-id <brand_id> [--receipt-out receipt.json]`

Notes for Brands V3:
- `brands-v3 get` and `query` are read-only commands.
- `create`, `update`, `bulk-create`, `bulk-update`, `get-or-create`, and `bulk-get-or-create` are reviewed-plan writes.
- `delete` and `bulk-delete` are irreversible reviewed-plan writes and also require `--ack-irreversible`.
- Official Wix docs say the Wix Stores app must be installed.
- Reads use `Read brands in catalog v3`.
- Writes use `Brand write in v3 catalog`.
- `brands-v3 query` returns up to `100` brands by default with `createdDate DESC` and `cursorPaging.limit 100`.
- `brands-v3 update` and `bulk-update` require the current `revision`.
- Deleting a brand automatically removes it from products that reference it.
- Get-or-create commands may create a brand when no matching name exists.
- This family is locally proven and still live-unverified.

## Read and manage Stores Catalog V3 ribbons

Use these commands to inspect Catalog V3 ribbons and keep writes inside the reviewed-plan flow.

- `wix-safe-agent-cli ribbons-v3 get --ribbon-id <ribbon_id>`
- `wix-safe-agent-cli ribbons-v3 query [--query-json '{"filter":{"name":{"$startsWith":"Sale"}}}']`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 create --ribbon-json '{"name":"Sale"}'`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 update --ribbon-id <ribbon_id> --ribbon-json '{"name":"Sale","revision":"1"}'`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 delete --ribbon-id <ribbon_id>`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 bulk-create --ribbons-json '[{"name":"Sale"}]'`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 bulk-delete --ribbon-ids-json '["<ribbon_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 bulk-update --ribbons-json '[{"id":"<ribbon_id>","name":"Sale","revision":"1"}]'`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 get-or-create --ribbon-name Sale`
- `wix-safe-agent-cli --plan-out plan.json ribbons-v3 bulk-get-or-create --ribbon-names-json '["Sale"]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json ribbons-v3 create --ribbon-json '{"name":"Sale"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json ribbons-v3 delete --ribbon-id <ribbon_id> [--receipt-out receipt.json]`

Notes for Ribbons V3:
- `ribbons-v3 get` and `query` are read-only commands.
- `create`, `update`, `bulk-create`, `bulk-update`, `get-or-create`, and `bulk-get-or-create` are reviewed-plan writes.
- `delete` and `bulk-delete` are irreversible reviewed-plan writes and also require `--ack-irreversible`.
- Official Wix docs say the Wix Stores app must be installed.
- Reads use `Read ribbons in v3 catalog`.
- Writes use `Ribbon write in v3 catalog`.
- `ribbons-v3 query` returns up to `100` ribbons by default with `createdDate DESC` and `cursorPaging.limit 100`.
- `ribbons-v3 update` and `bulk-update` require the current `revision`.
- Deleting a ribbon automatically removes it from products that reference it.
- Get-or-create commands may create a ribbon when no matching name exists.
- This family is locally proven and still live-unverified.

## Read and manage Stores Catalog V3 info sections

Use these commands to inspect Catalog V3 info sections and keep writes inside the reviewed-plan flow.

- `wix-safe-agent-cli stores-info-sections-v3 get --info-section-id <info_section_id>`
- `wix-safe-agent-cli stores-info-sections-v3 query [--query-json '{"filter":{"title":{"$startsWith":"Ship"}}}']`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 create --info-section-json @info-section.json`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 update --info-section-id <info_section_id> --info-section-json @info-section.json`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 delete --info-section-id <info_section_id>`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 bulk-create --info-sections-json @info-sections.json`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 bulk-delete --info-section-ids-json '["<info_section_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 bulk-update --info-sections-json @info-sections.json`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 get-or-create --info-section-json '{"uniqueName":"shipping","title":"Shipping Details"}'`
- `wix-safe-agent-cli --plan-out plan.json stores-info-sections-v3 bulk-get-or-create --info-sections-json '[{"uniqueName":"shipping","title":"Shipping Details"}]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-info-sections-v3 create --info-section-json @info-section.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-info-sections-v3 update --info-section-id <info_section_id> --info-section-json @info-section.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json stores-info-sections-v3 delete --info-section-id <info_section_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json stores-info-sections-v3 bulk-delete --info-section-ids-json '["<info_section_id>"]' [--receipt-out receipt.json]`

Notes for Stores Info Sections V3:
- `stores-info-sections-v3 get` and `query` are reads/helpers.
- `stores-info-sections-v3 create`, `update`, `bulk-create`, `bulk-update`, `get-or-create`, and `bulk-get-or-create` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `stores-info-sections-v3 delete` and `bulk-delete` are irreversible reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say reads use `Read info sections in v3 catalog` and writes use `Info section write in v3 catalog`.
- `stores-info-sections-v3 update` and `bulk-update` require the current info section `revision`.
- `stores-info-sections-v3 query` returns up to `100` items by default with `createdDate DESC` and `cursorPaging.limit 100`.
- Deleting an info section also removes it from products that use it, so recovery is manual only.
- Get-or-create commands retrieve by ID or `uniqueName`, and if the `uniqueName` does not exist, official docs require `uniqueName` and `title` to create the missing info section.
- This family is locally proven and still live-unverified.

## Read and manage Stores Catalog V3 customizations

Use these commands to inspect and manage Catalog V3 customizations.

- `wix-safe-agent-cli customizations-v3 get --customization-id <customization_id>`
- `wix-safe-agent-cli customizations-v3 query [--query-json '{"filter":{"name":{"$startsWith":"Gift"}}}']`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 create --customization-json @customization.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 update --customization-id <customization_id> --customization-json @customization.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 delete --customization-id <customization_id>`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 bulk-create --customizations-json @customizations.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 bulk-update --customizations-json @customizations.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 add-choices --customization-id <customization_id> --choices-json @choices.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 bulk-add-choices --customizations-json @customization-choices.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 remove-choices --customization-id <customization_id> --choices-json @choice-ids.json`
- `wix-safe-agent-cli --plan-out plan.json customizations-v3 set-choices --customization-id <customization_id> --choices-json @choices.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json customizations-v3 create --customization-json @customization.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json customizations-v3 delete --customization-id <customization_id>`

Notes for Customizations V3:
- `customizations-v3 get` and `query` are reads/helpers.
- `customizations-v3 create`, `update`, `bulk-create`, `bulk-update`, `add-choices`, and `bulk-add-choices` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `customizations-v3 delete`, `remove-choices`, and `set-choices` are irreversible reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say the Wix Stores app must be installed.
- Reads use `Read customizations in v3 catalog`; writes use `Customization write in v3 catalog`.
- `customizations-v3 update` and `bulk-update` require the current customization `revision`.
- `customizations-v3 query` returns up to `100` customizations by default with `createdDate DESC` and `cursorPaging.limit 100`.
- Deleting a customization also removes it from all products and variants that use it.
- Removing choices removes those choices from all products and variants that use them.
- This family is locally proven and still live-unverified.

## Manage Stores Catalog V3 categories

Use these commands to inspect and manage the Catalog V3 category tree and item/category relationships.

- `wix-safe-agent-cli categories get --category-id <category_id> [--tree-reference-json '{"appNamespace":"@wix/stores","treeKey":null}']`
- `wix-safe-agent-cli categories get-by-slug --slug <slug> [--tree-reference-json '{"appNamespace":"@wix/stores","treeKey":null}']`
- `wix-safe-agent-cli categories query [--query-json '{"filter":{"name":{"$startsWith":"Sale"}}}']`
- `wix-safe-agent-cli categories search [--search-json '{"includeHiddenCategories":true}']`
- `wix-safe-agent-cli categories count [--filter-json '{"hidden":{"$eq":false}}']`
- `wix-safe-agent-cli categories list-trees [--tree-reference-json '{"appNamespace":"@wix/stores","treeKey":null}']`
- `wix-safe-agent-cli categories get-arranged-items --category-id <category_id> [--tree-reference-json '{"appNamespace":"@wix/stores","treeKey":null}']`
- `wix-safe-agent-cli categories list-categories-for-item [--request-json '{"catalogItemId":"product-1"}']`
- `wix-safe-agent-cli categories list-categories-for-items [--request-json '{"catalogItemIds":["product-1","product-2"]}']`
- `wix-safe-agent-cli categories list-items-in-category --category-id <category_id> [--request-json '{"paging":{"limit":10}}']`
- `wix-safe-agent-cli categories create --category-json '{"name":"Sale"}'`
- `wix-safe-agent-cli categories update --category-id <category_id> --category-json '{"revision":"1","name":"Sale"}'`
- `wix-safe-agent-cli categories delete --category-id <category_id>`
- `wix-safe-agent-cli categories bulk-update --categories-json '[{"id":"cat-1","revision":"1","name":"Sale"}]'`
- `wix-safe-agent-cli categories update-visibility --request-json '{"categoryIds":["cat-1"],"visible":true}'`
- `wix-safe-agent-cli categories bulk-show --request-json '{"categoryIds":["cat-1"]}'`
- `wix-safe-agent-cli categories bulk-add-items-to-category --category-id <category_id> --request-json '{"itemIds":["item-1"]}'`
- `wix-safe-agent-cli categories bulk-add-item-to-categories --request-json '{"itemId":"item-1","categoryIds":["cat-1"]}'`
- `wix-safe-agent-cli categories bulk-remove-items-from-category --category-id <category_id> --request-json '{"itemIds":["item-1"]}'`
- `wix-safe-agent-cli categories bulk-remove-item-from-categories --request-json '{"itemId":"item-1","categoryIds":["cat-1"]}'`
- `wix-safe-agent-cli categories move --category-id <category_id> --request-json '{"afterCategoryId":"cat-0"}'`
- `wix-safe-agent-cli categories set-arranged-items --category-id <category_id> --request-json '{"items":[{"catalogItemId":"item-1"}]}'`

Notes for Categories:
- Reads/helper commands are immediate. Writes are reviewed-plan commands and require `--plan-in --apply --yes` for live changes.
- `delete`, `bulk-remove-items-from-category`, `bulk-remove-item-from-categories`, and `set-arranged-items` also require `--ack-irreversible`.
- Official Wix docs say the Wix Stores app must be installed and the family is Catalog V3-only.
- Reads use `Read categories`.
- Writes use the category write permissions in the official Wix docs.
- The request shape depends on the official `treeReference` with `appNamespace: "@wix/stores"` and `treeKey: null`.
- Hidden categories only appear when callers include `includeHiddenCategories: true` in query/search bodies.
- `update` and `bulk-update` require the current category revision.
- Deleting a category also deletes its subcategories.
- `get-by-slug` is marked Developer Preview by Wix.
- This family is locally proven and still live-unverified.

## Read and manage Stores Catalog V3 inventory items

Use these commands to inspect Catalog V3 inventory items, search or query them, and keep inventory writes inside the reviewed-plan flow.

- `wix-safe-agent-cli stores-inventory-items-v3 get --inventory-item-id <inventory_item_id>`
- `wix-safe-agent-cli stores-inventory-items-v3 query [--query-json '{"filter":{"locationId":{"$eq":"location-1"}}}']`
- `wix-safe-agent-cli stores-inventory-items-v3 search [--search-json '{"filter":{"variantId":{"$eq":"variant-1"}}}']`
- `wix-safe-agent-cli --plan-out plan.json stores-inventory-items-v3 create --inventory-item-json @inventory-item.json`
- `wix-safe-agent-cli --plan-out plan.json stores-inventory-items-v3 update --inventory-item-id <inventory_item_id> --inventory-item-json @inventory-item.json`
- `wix-safe-agent-cli --plan-out plan.json stores-inventory-items-v3 delete --inventory-item-id <inventory_item_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-inventory-items-v3 create --inventory-item-json @inventory-item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json stores-inventory-items-v3 update --inventory-item-id <inventory_item_id> --inventory-item-json @inventory-item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json stores-inventory-items-v3 delete --inventory-item-id <inventory_item_id> [--receipt-out receipt.json]`

Notes for Stores Inventory Items V3:
- `stores-inventory-items-v3 get`, `query`, and `search` are reads/helpers.
- `stores-inventory-items-v3 create` and `update` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `stores-inventory-items-v3 delete` is an irreversible reviewed-plan write that also requires `--ack-irreversible`.
- Official Wix docs say the Wix Stores app must be installed, reads use `Read inventory in v3 catalog`, and writes use `Inventory write in v3 catalog`.
- `stores-inventory-items-v3 update` requires the current inventory-item `revision`.
- Official Wix docs also say the combination of `variantId` and `locationId` must stay unique, query returns up to `1,000` items, search defaults to `createdDate DESC` with `cursorPaging.limit 100`, and the product read-only inventory field reflects the default location only.
- This family is locally proven and still live-unverified.

## Read Stores Catalog V3 inventory locations

Use these commands to inspect the inventory-relevant locations exposed by Wix Stores Catalog V3.

- `wix-safe-agent-cli stores-locations-v3 get --stores-location-id <stores_location_id>`
- `wix-safe-agent-cli stores-locations-v3 query [--query-json '{"filter":{"isDefault":{"$eq":true}}}']`

Notes for Stores Locations V3:
- `stores-locations-v3 get` and `query` are read-only commands.
- Official Wix docs say this family exists only for inventory-relevant locations and does not create or update them.
- The Wix Stores app must be installed.
- Only locations with `INVENTORY` in `locationTypes` appear here.
- The default location is used for inventory items that do not have a specific location assigned.
- Official Wix docs say location creation or updates belong in the Wix Locations API, not this family.
- This family is locally proven and still live-unverified.

## Check the current Stores catalog version

Use this command to detect whether the current site is using Wix Stores Catalog V1 or Catalog V3 before you pick a broader Stores flow.

- `wix-safe-agent-cli catalog-versioning get`

Notes for Catalog Versioning:
- `catalog-versioning get` is a read-only command.
- Official Wix docs say each site supports either Catalog V1 or Catalog V3, but not both.
- The endpoint takes no parameters. Authorization carries the site context.
- Official Wix docs also say the result is permanent for a given site, so one successful check is usually enough for a flow.
- The Wix Stores app must be installed.
- This family is locally proven and still live-unverified.

## Read and manage orders

Use these commands to inspect orders, search them, and keep every live order change inside the reviewed-plan flow.

- `wix-safe-agent-cli orders search [--search-json '{"filter":{"status":"PAID"}}']`
- `wix-safe-agent-cli orders get --order-id <order_id>`
- `wix-safe-agent-cli --plan-out plan.json orders create --order-json @order.json`
- `wix-safe-agent-cli --plan-out plan.json orders update --order-id <order_id> --order-json @order.json`
- `wix-safe-agent-cli --plan-out plan.json orders cancel --order-id <order_id> [--cancel-json @cancel.json]`
- `wix-safe-agent-cli --plan-out plan.json orders bulk-update --orders-json @orders-bulk-update.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json orders create --order-json @order.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json orders update --order-id <order_id> --order-json @order.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json orders cancel --order-id <order_id> [--cancel-json @cancel.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json orders bulk-update --orders-json @orders-bulk-update.json [--receipt-out receipt.json]`

Notes for Orders:
- `orders search` and `orders get` are reads.
- `orders create`, `orders update`, and `orders bulk-update` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `orders cancel` is an irreversible reviewed-plan write and also requires `--ack-irreversible`.
- Official Wix docs say this family uses Wix app or Wix user identity auth and `Manage Orders`.
- `orders create` is for manual orders or external systems.
- `orders update` only covers the documented subset of order fields.
- `orders bulk-update` supports up to `100` orders and only the documented fields.
- `orders cancel` changes status to `CANCELED`, has no automatic rollback, and may trigger buyer-email and restock side effects.

## Read and manage order billing actions

Use these commands to inspect refundability, preview refunds, authorize saved-payment-method charges, capture or void authorized payments, generate receipts, redeem gift cards, and process refunds through the reviewed-plan flow.

- `wix-safe-agent-cli order-billing get-order-refundability --order-id <order_id>`
- `wix-safe-agent-cli order-billing calculate-refund --order-id <order_id> --refund-items-json '{"lineItems":[{"lineItemId":"<line_item_id>","quantity":1}]}'`
- `wix-safe-agent-cli --plan-out plan.json order-billing authorize-charge-with-saved-payment-method --order-id <order_id> --amount-json '{"amount":"1"}' --currency USD [--delayed-capture-settings-json @delayed-capture.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json order-billing authorize-charge-with-saved-payment-method --order-id <order_id> --amount-json '{"amount":"1"}' --currency USD [--delayed-capture-settings-json @delayed-capture.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json order-billing capture-authorized-payments --order-id <order_id> --payments-json '[{"paymentId":"<payment_id>","amount":{"amount":"1"}}]'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json order-billing capture-authorized-payments --order-id <order_id> --payments-json '[{"paymentId":"<payment_id>","amount":{"amount":"1"}}]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json order-billing void-authorized-payments --order-id <order_id> --payment-ids-json '["<payment_id>"]'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json order-billing void-authorized-payments --order-id <order_id> --payment-ids-json '["<payment_id>"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json order-billing generate-receipts --order-id <order_id> --payment-ids-json '["<payment_id>"]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json order-billing generate-receipts --order-id <order_id> --payment-ids-json '["<payment_id>"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json order-billing redeem-gift-card --order-id <order_id> --gift-card-code <gift_card_code> --amount-json '{"amount":"20"}' --currency USD`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json order-billing redeem-gift-card --order-id <order_id> --gift-card-code <gift_card_code> --amount-json '{"amount":"20"}' --currency USD [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json order-billing refund-payments --order-id <order_id> --payment-refunds-json '[{"paymentId":"<payment_id>","amount":"5.00","externalRefund":true}]' [--refund-items-json @refund-items.json] [--side-effects-json @side-effects.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json order-billing refund-payments --order-id <order_id> --payment-refunds-json '[{"paymentId":"<payment_id>","amount":"5.00","externalRefund":true}]' [--refund-items-json @refund-items.json] [--side-effects-json @side-effects.json] [--receipt-out receipt.json]`

Notes for Order Billing:
- `get-order-refundability` is read-only and tells you whether a payment is `refundable`, `manuallyRefundable`, or `nonRefundable`.
- `calculate-refund` previews the refund total and breakdown before you call `refund-payments`.
- `authorize-charge-with-saved-payment-method` is a reviewed-plan write for orders that already have a saved payment method. Optional `delayedCaptureSettings` can schedule later capture or void behavior.
- `capture-authorized-payments` and `void-authorized-payments` are irreversible reviewed-plan writes. Official Wix docs say they only work on `AUTHORIZED` payments, and capture currently supports the full authorized amount only.
- `generate-receipts` is a reviewed-plan write with provider-response-only verification because receipt delivery and rendering happen outside this CLI. Official Wix docs currently mark it Developer Preview.
- `redeem-gift-card` is an irreversible reviewed-plan write that consumes gift card balance and is currently marked Developer Preview in official Wix docs.
- `refund-payments` is the reviewed-plan refund write. It needs `--plan-in --apply --yes --ack-irreversible` for live apply.
- Set `externalRefund: true` inside `--payment-refunds-json` when the refund was already handled outside Wix. This keeps the manual/provider-side path explicit.
- `refund-payments` can also restock inventory and send customer notifications when `sideEffects` asks for them.
- Verification is provider response plus a follow-up `get-order-refundability` reread for the payment-moving methods. No automatic rollback is promised.

## Read payment transactions

Use this command to inspect Cashier Payments transactions with the official Wix query filters.

- `wix-safe-agent-cli payments transactions-list [--from-created 2026-01-01T00:00:00Z] [--to-created 2026-01-31T23:59:59Z] [--limit 25] [--offset 0] [--order date:desc] [--status APPROVED] [--include-refunds]`

Notes for Payments:
- `payments transactions-list` is read-only.
- Official Wix docs expose this method as `GET /payments/v2/transactions`.
- Official Wix docs say the method retrieves transactions using query parameters and supports pagination.
- `--limit` follows the official maximum of `1000`; when omitted, Wix defaults to `10`.
- `--order` accepts only `date:asc` or `date:desc`; when omitted, Wix defaults to `date:desc`.
- `--status` can be repeated for more than one transaction status.
- `--currency` and `--app-id` are still exposed because the official method lists them, but Wix marks both filters deprecated with a target removal date of 2026-06-30.
- The official schema currently lists no custom permission scopes for this method. The command still uses the normal Wix token path and remains live-unverified.
- Payment-provider and checkout plugin surfaces stay outside the CLI command surface because they are plugin, hosted, or callback-driven rather than normal one-shot CLI calls.

## Read and manage benefit items

Use these commands to inspect benefit items and make plan-first item changes for the current site.

- `wix-safe-agent-cli benefit-items get --item-id <item_id>`
- `wix-safe-agent-cli benefit-items list`
- `wix-safe-agent-cli benefit-items query [--query-json '{"paging":{"limit":50}}']`
- `wix-safe-agent-cli benefit-items count [--filter-json '{"providerAppId":{"$eq":"<app_id>"}}']`
- `wix-safe-agent-cli --plan-out plan.json benefit-items create --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items update --item-id <item_id> --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items delete --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-create --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-update --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-delete --item-ids-json '["<item_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-delete-by-filter --filter-json '{"providerAppId":{"$eq":"<app_id>"}}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items create --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items update --item-id <item_id> --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items delete --item-id <item_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items bulk-create --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items bulk-update --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items bulk-delete --item-ids-json '["<item_id>"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items bulk-delete-by-filter --filter-json '{"providerAppId":{"$eq":"<app_id>"}}' [--receipt-out receipt.json]`

Notes for Benefit Items:
- `benefit-items get`, `list`, `query`, and `count` are reads.
- `benefit-items create`, `update`, `delete`, `bulk-create`, `bulk-update`, `bulk-delete`, and `bulk-delete-by-filter` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `benefit-items delete`, `bulk-delete`, and `bulk-delete-by-filter` are irreversible reviewed-plan writes and also require `--ack-irreversible`.
- Sites using this API must install the Pricing Plans app.
- `benefit-items get`, `list`, `query`, and `count` use Wix app or Wix user identity auth. Reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)` and writes use `Manage benefit programs`.
- `benefit-items query` defaults to paging limit `50`.
- `benefit-items list` returns up to `1000` items.
- `benefit-items update` and `benefit-items bulk-update` require the current `revision`.
- `benefit-items delete`, `bulk-delete`, and `bulk-delete-by-filter` remove the benefit association immediately and may affect currently active pools.
- This CLI refuses empty filters for `benefit-items bulk-delete-by-filter`.

## Read and manage benefit balances

Use these commands to inspect Benefit Programs balances and keep every live credit change inside the reviewed-plan flow.

- `wix-safe-agent-cli balances get --pool-id <pool_id>`
- `wix-safe-agent-cli balances list`
- `wix-safe-agent-cli balances query [--query-json '{"paging":{"limit":25}}']`
- `wix-safe-agent-cli --plan-out plan.json balances change --pool-id <pool_id> --change-json @change.json`
- `wix-safe-agent-cli --plan-out plan.json balances revert-change --transaction-id <transaction_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json balances change --pool-id <pool_id> --change-json @change.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json balances revert-change --transaction-id <transaction_id> [--receipt-out receipt.json]`

Notes for Balances:
- `balances get`, `list`, and `query` are reads.
- `balances change` and `balances revert-change` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- Sites using this API must install the Pricing Plans app.
- `balances get`, `list`, and `query` use Wix app or Wix user identity auth. Reads use `SCOPE.BENEFIT_PROGRAMS.READ (PII)` and writes use `Manage benefit programs`.
- `balances query` defaults to paging limit `50` and supports filters on `id`, `createdDate`, `beneficiary.memberId`, and `beneficiary.wixUserId`.
- `balances change` works on one `poolId` and verifies by provider response plus balance reread.
- `balances revert-change` is a specific official transaction undo path, not a blanket rollback promise. This boundary rereads the affected balance only when the provider response exposes a usable `poolId`.

## Read Wix Bookings Time Slots V2 availability

Use these commands to ask Wix which appointment, class event, or multi-service appointment slots are available before any booking write is attempted.

- `wix-safe-agent-cli bookings-time-slots-v2 list-availability --list-availability-json @list-availability.json`
- `wix-safe-agent-cli bookings-time-slots-v2 get-availability --get-availability-json @get-availability.json`
- `wix-safe-agent-cli bookings-time-slots-v2 list-event --list-event-json @list-event.json`
- `wix-safe-agent-cli bookings-time-slots-v2 get-event --event-id <event_id>`
- `wix-safe-agent-cli bookings-time-slots-v2 list-multi-service --list-multi-service-json @list-multi-service.json`
- `wix-safe-agent-cli bookings-time-slots-v2 get-multi-service --get-multi-service-json @get-multi-service.json`

Notes for Bookings Time Slots V2:
- `bookings-time-slots-v2 list-availability`, `get-availability`, `list-event`, `get-event`, `list-multi-service`, and `get-multi-service` are read-only commands.
- The single-service appointment commands support appointment-based service availability.
- The event commands support class session time slots. Official Wix docs mark `get-event` as Developer Preview.
- The multi-service commands support multi-service appointment availability for appointment-type services only.
- Official Wix docs say the Wix Bookings app must be installed on the site.
- Official Wix docs say the permission is `Read Bookings Calendar Availability` with scope `SCOPE.DC-BOOKINGS.READ-CALENDAR`.
- Official Wix docs list applicable identities `APP`, `MEMBER`, and `VISITOR`; this CLI keeps using its current normal auth path and remains live-unverified.
- This Time Slots V2 boundary does not claim broader Bookings coverage such as full course-flow, policy, attendance, waitlist, or calendar-family commands; those live in their own command families when shipped.

## Read Wix Bookings extended bookings

Use these commands to query and count extended bookings.

- `wix-safe-agent-cli bookings-reader-v2 query-extended-bookings --query-json @query.json`
- `wix-safe-agent-cli bookings-reader-v2 count-extended-bookings [--filter-json @filter.json]`

Notes for Bookings Reader V2:
- `query-extended-bookings` and `count-extended-bookings` are read-only commands.
- Official Wix docs say the Wix Bookings app must be installed on the site.
- Official Wix docs say there is no Get Extended Booking method, so callers should use Query Extended Bookings with a single booking ID in the filter when needed.
- Official Wix docs say query returns up to `100` bookings by default, sorts by `id ASC`, and uses `cursorPaging.limit 50`.
- Official Wix docs say course bookings use `scheduleId`, `withBookingAllowedActions` is optional, and date filters must use UTC.
- Official Wix docs list the permissions `Read bookings calendar - including participants`, `Manage Bookings`, and `Read Bookings - Including Participants`.
- `count-extended-bookings` sends `{"filter": {}}` when `--filter-json` is omitted.
- This boundary remains live-unverified.

## Read and manage Wix Bookings policies

Use these commands to inspect and change booking rules such as booking windows, cancellation rules, rescheduling rules, participant limits, and waitlist policy settings.

- `wix-safe-agent-cli bookings-policies get --booking-policy-id <booking_policy_id>`
- `wix-safe-agent-cli bookings-policies query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-policies count [--filter-json @filter.json]`
- `wix-safe-agent-cli bookings-policies strictest --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-policies create --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-policies update --booking-policy-id <booking_policy_id> --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-policies delete --booking-policy-id <booking_policy_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-policies set-default --booking-policy-id <booking_policy_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-policies create --policy-json @policy.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-policies delete --booking-policy-id <booking_policy_id> [--receipt-out receipt.json]`

Notes for Booking Policies:
- `get`, `query`, `count`, and `strictest` are read/helper commands.
- `create` and `update` are reviewed-plan writes.
- `delete` and `set-default` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say every Wix Bookings site has a default booking policy that can be updated but cannot be deleted before another policy is set as default.
- Official Wix docs say update requires the current `bookingPolicy.revision`.
- Official Wix docs say query defaults to `createdDate ASC` and `cursorPaging.limit 100`.
- Official Wix docs say daylight saving time can affect booking and cancellation policy windows.
- This family remains live-unverified.

## Read Wix Bookings policy snapshots

Use this command to retrieve the booking policy snapshot saved for one or more bookings.

- `wix-safe-agent-cli bookings-policy-snapshots list --booking-ids <booking_id_1,booking_id_2>`

Notes for Booking Policy Snapshots:
- `list` is a read-only command.
- Official Wix docs say the method retrieves policy snapshots by booking IDs.
- Official Wix docs say this method uses permission `Read Bookings - Public Data`.
- Official Wix docs say every booking with a related eCommerce order has exactly one policy snapshot, while bookings without a related eCommerce order do not have a policy snapshot.
- Official Wix docs say snapshots cannot be created with this API.
- The Booking Policy Service Plugin stays outside this CLI because it is a Developer Preview service-plugin surface hosted at `{DEPLOYMENT-URI}/v2/list-booking-policies`, not a normal Wix REST endpoint.
- This family remains live-unverified.

## Read and manage Wix Bookings attendance

Use these commands to check or update whether customers attended booking sessions.

- `wix-safe-agent-cli bookings-attendance get --attendance-id <attendance_id>`
- `wix-safe-agent-cli bookings-attendance query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-attendance count [--filter-json @filter.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-attendance set --attendance-json @attendance.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-attendance bulk-set --attendance-json @attendance.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-attendance delete --attendance-id <attendance_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-attendance bulk-delete --attendance-json @attendance.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-attendance set --attendance-json @attendance.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-attendance delete --attendance-id <attendance_id> [--receipt-out receipt.json]`

Notes for Bookings Attendance:
- `get`, `query`, and `count` are read/helper commands.
- `count` is Developer Preview and only works when the Authorization token identifies a site member.
- `set` and `bulk-set` are reviewed-plan writes.
- `delete` and `bulk-delete` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say query can look at attendance from a booking or session perspective.
- Official Wix docs say query returns up to `100` records, defaults to `id ASC`, and uses `cursorPaging.limit 50`.
- Official Wix docs say only one filter is processed per attendance query.
- Official Wix docs say Set Attendance validation is limited, so callers must validate attendee counts against attendance status and the booking participant count.
- This family remains live-unverified.

## Read and manage Wix Bookings waitlists

Use these commands to inspect waitlists, register members, remove registrations, or book a waitlisted member into the session.

- `wix-safe-agent-cli bookings-waitlist list --waiting-resources <session_id_1,session_id_2>`
- `wix-safe-agent-cli --plan-out plan.json bookings-waitlist register --request-json @request.json --ack-event-session`
- `wix-safe-agent-cli --plan-out plan.json bookings-waitlist leave --request-json @request.json --ack-event-session`
- `wix-safe-agent-cli --plan-out plan.json bookings-waitlist book --request-json @request.json --ack-event-session`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-waitlist register --request-json @request.json --ack-event-session [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-waitlist leave --request-json @request.json --ack-event-session [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-waitlist book --request-json @request.json --ack-event-session [--receipt-out receipt.json]`

Notes for Bookings Waitlist:
- All Waitlist methods are Developer Preview.
- `list` is a read/helper command and requires one or more waiting-resource session GUIDs.
- `register` is a reviewed-plan write and requires `--ack-event-session`.
- `leave` and `book` are reviewed-plan writes that require `--ack-event-session` and also require `--ack-irreversible`.
- Official Wix docs say waitlist functionality is currently limited to sessions with `type = EVENT`.
- Official Wix docs say `register` requires `waitingResource` and `formInfo`, while `leave` requires `registrationId` and `waitingResource`.
- Official Wix docs say `book` enrolls the waitlisted member, checks out the associated booking, and changes the registration status to `ENROLLED`.
- This family remains live-unverified.

## Read and manage Wix Calendar Schedules V3

Use these commands to inspect, create, update, or cancel Calendar schedules used by Bookings services, staff, and other Wix calendar integrations.

- `wix-safe-agent-cli calendar-schedules-v3 get --schedule-id <schedule_id>`
- `wix-safe-agent-cli calendar-schedules-v3 query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json calendar-schedules-v3 create --schedule-json @schedule.json`
- `wix-safe-agent-cli --plan-out plan.json calendar-schedules-v3 update --schedule-id <schedule_id> --schedule-json @schedule.json`
- `wix-safe-agent-cli --plan-out plan.json calendar-schedules-v3 cancel --schedule-id <schedule_id> [--request-json @cancel.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json calendar-schedules-v3 create --schedule-json @schedule.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json calendar-schedules-v3 update --schedule-id <schedule_id> --schedule-json @schedule.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-schedules-v3 cancel --schedule-id <schedule_id> [--request-json @cancel.json] [--receipt-out receipt.json]`

Notes for Calendar Schedules V3:
- `get` and `query` are read/helper commands.
- `create` and `update` are reviewed-plan writes.
- `cancel` is a reviewed-plan write that also requires `--ack-irreversible` because Wix says cancelled schedules cannot be reactivated, updated, or assigned new events, and cancelling a schedule cancels future events that belong to it.
- Official Wix docs say Bookings-visible schedules must use Wix Bookings app ID `13d21c63-b5ec-5912-8397-c3a5ddb27a97` in `schedule.appId`.
- Official Wix docs say update requires the current `schedule.revision`.
- Official Wix docs say query returns active schedules by default unless the caller filters by status, and supported filters are `id`, `externalId`, `appId`, and `status`.
- Schedule-created, schedule-updated, schedule-cancelled, and schedule-cloned events stay callback-only.
- This family remains live-unverified.

## Read Wix Calendar Schedule Time Frames V3

Use these commands to inspect the first and last event boundaries for one or more Calendar schedules.

- `wix-safe-agent-cli calendar-schedule-time-frames-v3 get --schedule-id <schedule_id> [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli calendar-schedule-time-frames-v3 list --ids-json '["<schedule_id>"]' [--time-zone <iana_time_zone>]`

Notes for Calendar Schedule Time Frames V3:
- `get` and `list` are read-only commands.
- Official Wix docs say `list` requires one to 100 schedule IDs in the `ids` query parameter.
- Schedule time frames cannot be updated through this API; the Schedule Time Frame Updated event stays callback-only.
- This family remains live-unverified.

## Read and manage Wix Calendar Events V3

Use these commands to inspect or manage Business Management Calendar events. This is separate from Wix Events & Tickets, which uses the `events-v3` command family.

- `wix-safe-agent-cli calendar-events-v3 get --event-id <event_id> [--fields-json '["PI_FIELDS"]'] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli calendar-events-v3 query [--query-json @query.json] [--from-local-date <local_date_time>] [--to-local-date <local_date_time>] [--recurrence-type-json '["NONE"]'] [--fields-json '["PI_FIELDS"]'] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli calendar-events-v3 list --event-ids-json '["<event_id>"]' [--fields-json '["PI_FIELDS"]'] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli calendar-events-v3 list-by-contact --contact-id <contact_id> --from-local-date <local_date_time> --to-local-date <local_date_time> [--sort-json @sort.json] [--cursor-paging-json @cursor.json] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli calendar-events-v3 list-by-member --member-id <member_id> --from-local-date <local_date_time> --to-local-date <local_date_time> [--event-ids-json '["<event_id>"]'] [--sort-json @sort.json] [--cursor-paging-json @cursor.json] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 create --event-json @event.json [--idempotency-key <uuid>] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 update --event-id <event_id> --event-json @event.json [--participant-notification-json @notification.json] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-create --events-json @events.json [--return-entity true] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-update --events-json @events.json [--participant-notification-json @notification.json] [--return-entity true] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 cancel --event-id <event_id> [--participant-notification-json @notification.json] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-events-v3 cancel --event-id <event_id> [--participant-notification-json @notification.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-cancel --event-ids-json '["<event_id>"]' [--participant-notification-json @notification.json] [--return-entity true] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-events-v3 bulk-cancel --event-ids-json '["<event_id>"]' [--participant-notification-json @notification.json] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 restore-defaults --event-id <event_id> --fields-json '["TIME"]' [--participant-notification-json @notification.json] [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-events-v3 restore-defaults --event-id <event_id> --fields-json '["TIME"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 split-recurring --recurring-event-id <event_id> --split-local-date <local_date_time> [--time-zone <iana_time_zone>]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-events-v3 split-recurring --recurring-event-id <event_id> --split-local-date <local_date_time> [--receipt-out receipt.json]`

Notes for Calendar Events V3:
- `get`, `query`, `list`, `list-by-contact`, and `list-by-member` are reads/helpers.
- `create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `cancel`, `bulk-cancel`, `restore-defaults`, and `split-recurring` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say `create` requires `event.scheduleId`, `event.start.localDate`, and `event.end.localDate`; recurring master events also require `recurrenceRule.frequency` and `recurrenceRule.days`.
- Official Wix docs say `update` requires the current `event.revision`.
- Official Wix docs limit `list` to 100 event IDs, and bulk create/update/cancel to 50 events or event IDs.
- Official Wix docs say contact/member event listing uses a one-year maximum date window and must use a date window unless cursor paging or event IDs are supplied.
- Event Created, Event Updated, Event Cancelled, and Event Recurring Split stay callback-only.
- This family remains live-unverified.

## Read Wix Calendar Event Views V3

Use this command to inspect how far into the future the current Calendar event view is complete.

- `wix-safe-agent-cli calendar-event-views-v3 get`

Notes for Calendar Event Views V3:
- `get` is a read-only command.
- Official Wix docs say it returns the current event view, including `eventsView.endDate` and `eventsView.futureDurationInDays`.
- Official Wix docs say it does not return event details. Use `calendar-events-v3 query` with `eventsView.endDate` as `toLocalDate` to retrieve events in the view.
- Official Wix docs say an event view is complete for at least one full year into the future, cannot be manually extended, and cannot be updated.
- Events View Extended and Events View Projection Updated stay callback-only.
- This family remains live-unverified.

## Read and manage Wix Calendar Participations V3

Use these commands to inspect or manage Calendar participation records for events and schedules. Do not use them to mutate participation details that Wix Bookings manages automatically.

- `wix-safe-agent-cli calendar-participations-v3 get --participation-id <participation_id>`
- `wix-safe-agent-cli calendar-participations-v3 query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json calendar-participations-v3 create --participation-json @participation.json`
- `wix-safe-agent-cli --plan-out plan.json calendar-participations-v3 update --participation-id <participation_id> --participation-json @participation.json`
- `wix-safe-agent-cli --plan-out plan.json calendar-participations-v3 delete --participation-id <participation_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json calendar-participations-v3 delete --participation-id <participation_id> [--receipt-out receipt.json]`

Notes for Calendar Participations V3:
- `get` and `query` are reads/helpers.
- `create` and `update` are reviewed-plan writes.
- `delete` is a reviewed-plan write that also requires `--ack-irreversible`.
- Official Wix docs say create, update, and delete automatically update the corresponding event `participants` and `remainingCapacity`.
- Official Wix docs say `update` requires the current `participation.revision`.
- Official Wix docs say each participation targets either an `eventId` or `scheduleId`, `partySize` must be between 1 and 1000, and `externalId` is immutable.
- Official Wix docs say `query` defaults to `createdDate DESC` with `cursorPaging.limit` 50 and supports filters for `id`, `eventId`, `scheduleId`, and `externalId`.
- Official Wix docs warn not to create, update, or delete participations while extending Wix Bookings because Wix Bookings manages participation details automatically.
- Participation Created, Participation Deleted, and Participation Updated stay callback-only.
- This family remains live-unverified.

## Calendar Skills / Default Business Hours

There is no `calendar-skills` command. Official Wix Calendar Skills docs describe a recipe for configuring Wix Bookings default business hours by using existing Calendar APIs.

Use the shipped Calendar commands for that recipe:

- `wix-safe-agent-cli calendar-schedules-v3 query --query-json @business-schedule-query.json`
- `wix-safe-agent-cli calendar-events-v3 query --query-json @working-hours-query.json --recurrence-type-json '["MASTER"]'`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-update --events-json @working-hours-updates.json`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-cancel --event-ids-json '["<event_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json calendar-events-v3 bulk-create --events-json @working-hours-events.json`

Notes for Calendar Skills / Default Business Hours:
- This is a docs-only boundary, not a callable API family.
- Official Wix docs say the Wix Bookings app must be installed, and default business hours appear in the Bookings dashboard under "Set default hours".
- Official Wix docs say the universal business schedule external ID is `4e0579a5-491e-4e70-a872-d097eed6e520`.
- Official Wix docs say to query existing `WORKING_HOURS` MASTER events before writing, because Wix Bookings creates default hours on installation and creating new hours without handling existing hours can cause duplicates.
- Use `calendar-events-v3 bulk-update` to update existing hours when possible; use `bulk-cancel` and `bulk-create` only when replacing hours.
- The underlying Calendar Events V3 commands keep their existing reviewed-plan write gates and `--ack-irreversible` requirement for `bulk-cancel`.

## Captcha

There is no `captcha authorize` command in this CLI.

Official Wix Captcha docs expose a Developer Preview Authorize method for Wix site or Blocks app backend code after the Wix reCAPTCHA element generates a token. The same official introduction says Wix Headless or REST API users can't use this API. Because this tool is a REST-based safe CLI, Captcha is tracked as gated and non-callable here instead of exposing a command that would not be valid for this client type.

## Read and manage Wix Bookings External Calendar V2

Use these commands to inspect external calendar providers and connections, connect accounts, adjust sync settings, list external events, or disconnect a connection.

- `wix-safe-agent-cli bookings-external-calendars-v2 list-providers`
- `wix-safe-agent-cli bookings-external-calendars-v2 list-connections [--query-json @query.json]`
- `wix-safe-agent-cli bookings-external-calendars-v2 get-connection --connection-id <connection_id>`
- `wix-safe-agent-cli bookings-external-calendars-v2 list-calendars --connection-id <connection_id>`
- `wix-safe-agent-cli bookings-external-calendars-v2 list-events --from <from_iso> --to <to_iso> [--schedule-ids <schedule_id_1,schedule_id_2>] [--fieldsets OWN_PI] [--partial-failure]`
- `wix-safe-agent-cli --plan-out plan.json bookings-external-calendars-v2 connect-by-credentials --request-json @request.json --ack-external-credentials`
- `wix-safe-agent-cli --plan-out plan.json bookings-external-calendars-v2 connect-by-oauth --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-external-calendars-v2 update-sync-config --connection-id <connection_id> --request-json @sync-config.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-external-calendars-v2 disconnect --connection-id <connection_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-external-calendars-v2 connect-by-credentials --request-json @request.json --ack-external-credentials [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-external-calendars-v2 connect-by-oauth --request-json @request.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-external-calendars-v2 update-sync-config --connection-id <connection_id> --request-json @sync-config.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-external-calendars-v2 disconnect --connection-id <connection_id> [--receipt-out receipt.json]`

Notes for Bookings External Calendar V2:
- Provider, connection, calendar, and event commands are read/helper commands.
- `connect-by-credentials`, `connect-by-oauth`, and `update-sync-config` are reviewed-plan writes.
- `connect-by-credentials` requires `--ack-external-credentials` and redacts secret fields such as `password` in plans and receipts.
- `disconnect` is a reviewed-plan write that also requires `--ack-irreversible` because Wix says it deletes Wix calendar events from the external calendar.
- Official Wix docs say all methods require `Manage External Calendars`.
- Official Wix docs say providers determine whether OAuth, credentials, or both are supported.
- Official Wix docs say `list-events` requires both `from` and `to` unless the caller supplies `cursorPaging.cursor`, and PI fields such as title require `OWN_PI`.
- This family remains live-unverified.

## Read and manage Wix Bookings Service Options and Variants

Use these commands to inspect or manage custom service options and variants used during booking flows.

- `wix-safe-agent-cli bookings-service-options-v1 get --service-options-id <service_options_id>`
- `wix-safe-agent-cli bookings-service-options-v1 get-by-service-id --service-id <service_id>`
- `wix-safe-agent-cli bookings-service-options-v1 query [--query-json @query.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-service-options-v1 create --options-json @options.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-service-options-v1 update --service-options-id <service_options_id> --options-json @options.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-service-options-v1 delete --service-options-id <service_options_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-service-options-v1 clone --clone-from-id <service_options_id> --request-json @request.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-service-options-v1 create --options-json @options.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-service-options-v1 update --service-options-id <service_options_id> --options-json @options.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-service-options-v1 delete --service-options-id <service_options_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-service-options-v1 clone --clone-from-id <service_options_id> --request-json @request.json [--receipt-out receipt.json]`

Notes for Bookings Service Options and Variants:
- `get`, `get-by-service-id`, and `query` are read/helper commands.
- `create`, `update`, and `clone` are reviewed-plan writes.
- `delete` is a reviewed-plan write that also requires `--ack-irreversible` because deleting service options removes varied pricing from the service.
- Official Wix docs say only one `serviceOptionsAndVariants` object is allowed per service and only one option is currently supported per object.
- Official Wix docs say variants are not automatically calculated during create; callers must manually define every variant.
- Official Wix docs say update requires the current `serviceOptionsAndVariants.revision`.
- Created, deleted, and updated events stay callback-only.
- This family remains live-unverified.

## Use Wix Bookings course flows

Use the shipped Bookings commands together for course bookings. Wix documents courses as an end-to-end booking flow, not as a separate course API family.

- `wix-safe-agent-cli bookings-services-v2 query --query-json @course-services-query.json`
- `wix-safe-agent-cli bookings-service-options-v1 get-by-service-id --service-id <service_id>`
- `wix-safe-agent-cli bookings-reader-v2 query-extended-bookings --query-json @course-bookings-query.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 create --booking-json @course-booking.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 confirm-or-decline --booking-id <booking_id> --request-json @decision.json`

Notes for Bookings course flows:
- Course service setup and lookup use `bookings-services-v2`; official Wix docs put course start/end and capacity data on the service, including `service.schedule`, `defaultCapacity`, and `bookingPolicy.bookAfterStart`.
- Varied course options and pricing use `bookings-service-options-v1 get-by-service-id`.
- Course capacity is checked by querying existing bookings with `bookings-reader-v2 query-extended-bookings`, filtering by `bookedEntity.item.schedule.serviceId`, summing `attendance.numberOfAttendees`, and comparing the result with the service `defaultCapacity`.
- Course bookings are created with `bookings-writer-v2 create`; official Wix docs say course create requests specify `booking.bookedEntity.schedule.scheduleId`.
- Official Wix docs say Time Slots V2 supports appointments, class event time slots, and multi-service appointments. Course availability belongs to the end-to-end course flow instead.
- Form summary and checkout URL steps remain in their own Forms and eCommerce coverage rows; this tool does not hide those dependencies inside a generic course command.
- This flow remains live-unverified.

## Read and manage Wix Bookings Writer V2 bookings

Use these commands to create bookings, manage booking lifecycle changes, work with multi-service bookings, and support anonymous customer booking links.

- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 create --booking-json @booking.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 bulk-create --bookings-json @bookings.json`
- `wix-safe-agent-cli bookings-writer-v2 bulk-calculate-allowed-actions --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 bulk-confirm-or-decline --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 confirm-or-decline --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 confirm --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 decline --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 cancel --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 reschedule --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 mark-pending --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 set-submission-id --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 update-extended-fields --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 update-participants --booking-id <booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 create-multi-service --multi-service-booking-json @multi-service-booking.json`
- `wix-safe-agent-cli bookings-writer-v2 get-multi-service --multi-service-booking-id <multi_service_booking_id>`
- `wix-safe-agent-cli bookings-writer-v2 get-multi-service-availability --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 add-to-multi-service --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 remove-from-multi-service --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 cancel-multi-service --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 confirm-multi-service --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 decline-multi-service --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 reschedule-multi-service --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 mark-multi-service-pending --multi-service-booking-id <multi_service_booking_id> --request-json @request.json`
- `wix-safe-agent-cli bookings-writer-v2 bulk-get-multi-service-allowed-actions --request-json @request.json`
- `wix-safe-agent-cli bookings-writer-v2 get-anonymous-action-token --booking-id <booking_id>`
- `wix-safe-agent-cli bookings-writer-v2 get-anonymous --token <anonymous_token>`
- `wix-safe-agent-cli bookings-writer-v2 get-service-anonymous --token <anonymous_token>`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 cancel-anonymous --token <anonymous_token> --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-writer-v2 reschedule-anonymous --token <anonymous_token> --request-json @request.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-writer-v2 create --booking-json @booking.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-writer-v2 cancel --booking-id <booking_id> --request-json @request.json [--receipt-out receipt.json]`

Notes for Bookings Writer V2:
- Multi-service reads, allowed-action helpers, anonymous reads, and anonymous token generation are read/helper commands.
- Booking create, status changes, reschedules, participant updates, extended-field updates, and multi-service changes are reviewed-plan writes.
- `bulk-create` is capped at `12` booking requests before the CLI sends anything to Wix.
- Cancel, decline, reschedule, participant-changing, remove-from-multi-service, bulk confirm/decline, and anonymous mutation commands also require `--ack-irreversible`.
- Official Wix docs say to check Time Slots V2 before creating or rescheduling bookings to reduce failed calls and double-booking conflicts.
- Multi-service bookings support 2-8 sequential appointment bookings at one business location. Courses and classes are not supported in multi-service bookings.
- Anonymous booking tokens are credentials. The anonymous read and mutation commands use the token itself instead of the normal auth header.
- Single-service booking reads stay in Bookings Reader V2. Attendance stays in the Attendance API. Payment status normally syncs from eCommerce checkout/orders unless a custom checkout flow is used.
- This family remains live-unverified.

## Read and manage Wix Bookings services

Use these commands to inspect service setup, query helper records, and make reviewed-plan service changes.

- `wix-safe-agent-cli bookings-services-v2 get --service-id <service_id>`
- `wix-safe-agent-cli bookings-services-v2 query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-services-v2 search [--search-json @search.json]`
- `wix-safe-agent-cli bookings-services-v2 count [--filter-json @filter.json]`
- `wix-safe-agent-cli bookings-services-v2 query-policies [--request-json @request.json]`
- `wix-safe-agent-cli bookings-services-v2 query-locations [--request-json @request.json]`
- `wix-safe-agent-cli bookings-services-v2 query-categories [--request-json @request.json]`
- `wix-safe-agent-cli bookings-services-v2 validate-slug [--request-json @request.json]`
- `wix-safe-agent-cli bookings-services-v2 list-add-on-groups-by-service-id [--request-json @request.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 create --service-json @service.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 update --service-id <service_id> --service-json @service.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 delete --service-id <service_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 bulk-create --services-json @services.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 bulk-update --services-json @services.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 bulk-update-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 bulk-delete --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 bulk-delete-by-filter --request-json @request.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 set-service-locations --service-id <service_id> --request-json @locations.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 enable-pricing-plans --service-id <service_id> --request-json @pricing-plans.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 disable-pricing-plans --service-id <service_id> --request-json @pricing-plans.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 set-custom-slug --service-id <service_id> --request-json @slug.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 clone --request-json @clone.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 create-add-on-group --request-json @add-on-group.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 delete-add-on-group --request-json @add-on-group.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 set-add-ons-for-group --request-json @add-ons.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-services-v2 update-add-on-group --request-json @add-on-group.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-services-v2 create --service-json @service.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-services-v2 delete --service-id <service_id> [--receipt-out receipt.json]`

Notes for Bookings Services V2:
- Read/helper commands are live calls in this boundary; write commands are reviewed-plan dry-runs until applied with `--plan-in --apply --yes`.
- `delete`, `bulk-delete`, `bulk-delete-by-filter`, `set-service-locations`, `disable-pricing-plans`, `delete-add-on-group`, and `set-add-ons-for-group` also require `--ack-irreversible`.
- Official Wix docs say the Wix Bookings app must be installed. Write methods use `Manage Bookings`.
- Service create requires the official core service fields. Appointment services need capacity `1` and at least one staff member.
- Bulk create and bulk update are capped at `100` services in this CLI before the request is sent.
- `set-service-locations` replaces the service's locations. `disable-pricing-plans` can make a service unbookable when pricing plans were the only payment option.
- Service created, deleted, and updated events are callback-only and are not CLI commands.
- This family remains live-unverified.

## Read and manage Wix Bookings resources

Use these commands to inspect and manage bookable rooms, equipment, assets, or other non-staff resources.

- `wix-safe-agent-cli bookings-resources-v2 get --resource-id <resource_id>`
- `wix-safe-agent-cli bookings-resources-v2 query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-resources-v2 search [--search-json @search.json]`
- `wix-safe-agent-cli bookings-resources-v2 count [--filter-json @filter.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 create --resource-json @resource.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 update --resource-id <resource_id> --resource-json @resource.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 delete --resource-id <resource_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 bulk-create --resources-json @resources.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 bulk-update --resources-json @resources.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resources-v2 bulk-delete --ids-json @resource-ids.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-resources-v2 create --resource-json @resource.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-resources-v2 delete --resource-id <resource_id> [--receipt-out receipt.json]`

Notes for Bookings Resources V2:
- `bookings-resources-v2 get`, `query`, `search`, and `count` are read/helper commands.
- `create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes.
- `delete` and `bulk-delete` also require `--ack-irreversible` because Wix cancels resource schedules during deletion.
- Official Wix docs say the Wix Bookings app must be installed. Reads use `Read Bookings - Public Data`; writes use `Manage Bookings`.
- Create requires `resource.name`. Update requires `resource.id` and the current `resource.revision`.
- Bulk create, update, and delete are capped at `50` resources or IDs in this CLI before the request is sent.
- Query and search return up to `100` resources. Resource Types V2 remains a separate family.
- Official Wix docs say not to use Resources V2 to manage staff resources because Wix automatically creates and manages staff resources.
- This family remains live-unverified.

## Read and manage Wix Bookings resource types

Use these commands to inspect and manage resource classifications such as rooms, equipment, or vehicles.

- `wix-safe-agent-cli bookings-resource-types-v2 get --resource-type-id <resource_type_id>`
- `wix-safe-agent-cli bookings-resource-types-v2 query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-resource-types-v2 count [--filter-json @filter.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-resource-types-v2 create --resource-type-json @resource-type.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resource-types-v2 update --resource-type-id <resource_type_id> --resource-type-json @resource-type.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-resource-types-v2 delete --resource-type-id <resource_type_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-resource-types-v2 create --resource-type-json @resource-type.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-resource-types-v2 delete --resource-type-id <resource_type_id> [--receipt-out receipt.json]`

Notes for Bookings Resource Types V2:
- `bookings-resource-types-v2 get`, `query`, and `count` are read/helper commands.
- `create` and `update` are reviewed-plan writes.
- `delete` also requires `--ack-irreversible` because Wix deletes all connected resources when a resource type is deleted.
- Official Wix docs say the Wix Bookings app must be installed. Reads use `Read Bookings - Public Data`; `get` also lists `Read Bookings Calendar`. Writes use `Manage Bookings`.
- Create requires `resourceType.name`. Update requires `resourceType.id` and the current `resourceType.revision`.
- Query returns up to `100` resource types.
- Official Wix docs say staff resource types are automatically managed by Wix, so do not use this family to manage staff.
- This family remains live-unverified.

## Read and manage Wix Bookings staff members

Use these commands to inspect staff, create or update staff records, assign working-hour schedules, manage staff/user links, update tags, and handle deleted staff records in the trash bin.

- `wix-safe-agent-cli bookings-staff-members get --staff-member-id <staff_member_id> [--field RESOURCE_DETAILS]`
- `wix-safe-agent-cli bookings-staff-members query [--query-json @query.json]`
- `wix-safe-agent-cli bookings-staff-members search --search-json @search.json`
- `wix-safe-agent-cli bookings-staff-members count [--filter-json @filter.json]`
- `wix-safe-agent-cli bookings-staff-members get-deleted --staff-member-id <staff_member_id> [--field RESOURCE_DETAILS]`
- `wix-safe-agent-cli bookings-staff-members list-deleted [--field RESOURCE_DETAILS] [--limit 50] [--cursor <cursor>]`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members create --staff-member-json @staff-member.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members update --staff-member-id <staff_member_id> --staff-member-json @staff-member.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members delete --staff-member-id <staff_member_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members assign-working-hours-schedule --staff-member-id <staff_member_id> --schedule-id <schedule_id>`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members bulk-update-tags --tags-json @tags.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members bulk-update-tags-by-filter --tags-filter-json @tags-filter.json`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members connect-to-user --staff-member-id <staff_member_id> [--connect-json @connect.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members disconnect-from-user --staff-member-id <staff_member_id> [--disconnect-json @disconnect.json]`
- `wix-safe-agent-cli --plan-out plan.json bookings-staff-members remove-from-trash --staff-member-id <staff_member_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json bookings-staff-members create --staff-member-json @staff-member.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json bookings-staff-members remove-from-trash --staff-member-id <staff_member_id> [--receipt-out receipt.json]`

Notes for Bookings Staff Members:
- `get`, `query`, `search`, `count`, `get-deleted`, and `list-deleted` are read/helper commands.
- `create`, `update`, `assign-working-hours-schedule`, `bulk-update-tags`, `bulk-update-tags-by-filter`, `connect-to-user`, and `disconnect-from-user` are reviewed-plan writes.
- `delete` also requires `--ack-irreversible` because Wix deletes the staff member's associated resource. `remove-from-trash` also requires `--ack-irreversible` because it permanently removes the deleted staff member.
- Official Wix docs say the Wix Bookings app must be installed. Writes use `Manage Bookings`; read pages list `BOOKINGS.STAFF_MEMBER_READ`.
- Update requires `staffMember.id` and the current `staffMember.revision`.
- Query and search return up to `100` staff members. Bulk tag update by IDs supports up to `100` staff members. Bulk tag update by filter is asynchronous and returns a job ID.
- Wix automatically manages staff resources and staff resource types, so keep staff work in this family instead of using Resources V2 or Resource Types V2.
- This family remains live-unverified.

## Read and manage coupons

Use these commands to inspect coupons, run bounded queries, and make plan-first coupon changes with the installed-app gate kept explicit.

- `wix-safe-agent-cli coupons get --coupon-id <coupon_id>`
- `wix-safe-agent-cli coupons query [--query-json '{"paging":{"limit":25}}']`
- `wix-safe-agent-cli --plan-out plan.json coupons create --coupon-json @coupon.json`
- `wix-safe-agent-cli --plan-out plan.json coupons update --coupon-id <coupon_id> --coupon-json @coupon.json`
- `wix-safe-agent-cli --plan-out plan.json coupons delete --coupon-id <coupon_id>`
- `wix-safe-agent-cli --plan-out plan.json coupons bulk-create --coupons-json @coupons.json`
- `wix-safe-agent-cli --plan-out plan.json coupons bulk-delete --coupon-ids-json '["<coupon_id>"]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json coupons create --coupon-json @coupon.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json coupons update --coupon-id <coupon_id> --coupon-json @coupon.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json coupons delete --coupon-id <coupon_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json coupons bulk-create --coupons-json @coupons.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json coupons bulk-delete --coupon-ids-json '["<coupon_id>"]' [--receipt-out receipt.json]`

Notes for Coupons:
- `coupons get` and `query` are reads.
- `coupons create`, `update`, and `bulk-create` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `coupons delete` and `bulk-delete` are irreversible reviewed-plan writes and also require `--ack-irreversible`.
- Official Wix docs say the site must have one of `stores`, `bookings`, `events`, or `pricingPlans` installed. This CLI checks that with `app-instance get` before the coupon request.
- Official Wix docs say all coupon methods use `Manage Coupons`.
- `coupons query` returns at most 100 coupons per request.
- Coupon codes are case and space sensitive, and only one coupon can be applied per order.
- Official coupon events remain callback-only in this tool.

## Read and manage gift cards

Use these commands to inspect gift cards, search or count them with official Wix filters, and keep every live write inside the reviewed-plan flow.

- `wix-safe-agent-cli gift-cards get --gift-card-id <gift_card_id>`
- `wix-safe-agent-cli gift-cards query [--query-json '{"query":{"filter":{"status":{"$eq":"ACTIVE"}},"cursorPaging":{"limit":25}}}']`
- `wix-safe-agent-cli gift-cards search [--search-json '{"search":{"expression":"summer"}}']`
- `wix-safe-agent-cli gift-cards count [--filter-json '{"status":{"$eq":"ACTIVE"}}']`
- `wix-safe-agent-cli --plan-out plan.json gift-cards create --gift-card-json @gift-card.json`
- `wix-safe-agent-cli --plan-out plan.json gift-cards disable --gift-card-id <gift_card_id>`
- `wix-safe-agent-cli --plan-out plan.json gift-cards send-email --gift-card-id <gift_card_id> [--recipient-email owner@example.com]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json gift-cards create --gift-card-json @gift-card.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json gift-cards disable --gift-card-id <gift_card_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json gift-cards send-email --gift-card-id <gift_card_id> [--recipient-email owner@example.com] [--receipt-out receipt.json]`

Notes for Gift Cards:
- `gift-cards get`, `query`, `search`, and `count` are reads.
- `gift-cards create`, `disable`, and `send-email` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `gift-cards disable` is irreversible and also requires `--ack-irreversible`.
- Official Wix docs say this family needs the Wix Gift Card app installed and uses `Manage eCommerce - all permissions`.
- `gift-cards send-email` also needs a premium site plan. This command proves provider acceptance plus gift-card readback, not inbox delivery.
- Gift card codes are only fully visible in the create response. Other API responses obfuscate the code.
- `gift-cards count` is currently marked Developer Preview in the official docs.
- `gift-cards create` accepts either a raw `giftCard` object or a full official create body.
- The deprecated list-by-email method is intentionally not shipped in this tool.

## Read and manage donation campaigns

Use these commands to inspect fundraiser setup, read campaign metrics, and keep every live donation-campaign write inside the reviewed-plan flow.

- `wix-safe-agent-cli donation-campaigns get --donation-campaign-id <campaign_id>`
- `wix-safe-agent-cli donation-campaigns get-metrics --donation-campaign-id <campaign_id>`
- `wix-safe-agent-cli donation-campaigns query [--query-json '{"query":{"filter":{"archived":{"$eq":false}},"cursorPaging":{"limit":25}}}']`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns create --donation-campaign-json @donation-campaign.json`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns update --donation-campaign-id <campaign_id> --donation-campaign-json @donation-campaign.json`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns bulk-create --donation-campaigns-json @donation-campaigns.json`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns bulk-update --donation-campaigns-json @donation-campaigns.json`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns bulk-update-tags --update-tags-json '{"ids":["<campaign_id>"],"assignTags":["vip"]}'`
- `wix-safe-agent-cli --plan-out plan.json donation-campaigns bulk-update-tags-by-filter --update-tags-json '{"filter":{"archived":{"$eq":false}},"assignTags":["vip"]}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns create --donation-campaign-json @donation-campaign.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns update --donation-campaign-id <campaign_id> --donation-campaign-json @donation-campaign.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns bulk-create --donation-campaigns-json @donation-campaigns.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns bulk-update --donation-campaigns-json @donation-campaigns.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns bulk-update-tags --update-tags-json '{"ids":["<campaign_id>"],"assignTags":["vip"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json donation-campaigns bulk-update-tags-by-filter --update-tags-json '{"filter":{"archived":{"$eq":false}},"assignTags":["vip"]}' [--receipt-out receipt.json]`

Notes for Donation Campaigns:
- `donation-campaigns get`, `get-metrics`, and `query` are reads.
- `donation-campaigns create`, `update`, `bulk-create`, `bulk-update`, `bulk-update-tags`, and `bulk-update-tags-by-filter` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- Official Wix docs say the site must have Wix Donations installed and all methods use `Manage Donation Campaigns`.
- `create` and `bulk-create` require `customAmountEnabled`, `predefinedDonationAmounts`, or both.
- Official docs say campaign status is automatic, so this tool refuses manual `status` updates.
- `update` and `bulk-update` require the current `revision`, and verification expects the campaign revision to change after apply.
- `query` defaults to `createdDate ASC` with `cursorPaging.limit 100`.
- `get-metrics` needs a configured `campaignGoal`, returns aggregated totals only, and stays in the site's default currency.
- `bulk-update-tags-by-filter` is async and verification proves returned `jobId` only. Follow up with `async-jobs get` or `async-jobs list-items`.
- Official docs allow an empty filter for `bulk-update-tags-by-filter`, but this boundary refuses empty-filter all-campaign retagging.

## Read and manage benefit items

Use these commands to inspect Benefit Programs items and keep every live item change inside the reviewed-plan flow.

- `wix-safe-agent-cli benefit-items get --item-id <item_id>`
- `wix-safe-agent-cli benefit-items list`
- `wix-safe-agent-cli benefit-items query [--query-json '{"paging":{"limit":25}}']`
- `wix-safe-agent-cli benefit-items count [--filter-json '{"providerAppId":{"$eq":"app-123"}}']`
- `wix-safe-agent-cli --plan-out plan.json benefit-items create --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items update --item-id <item_id> --item-json @item.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items delete --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-create --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-update --items-json @items.json`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-delete --item-ids-json '["<item_id>"]'`
- `wix-safe-agent-cli --plan-out plan.json benefit-items bulk-delete-by-filter --filter-json '{"providerAppId":{"$eq":"app-123"}}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items create --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items update --item-id <item_id> --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items delete --item-id <item_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items bulk-create --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json benefit-items bulk-update --items-json @items.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items bulk-delete --item-ids-json '["<item_id>"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json benefit-items bulk-delete-by-filter --filter-json '{"providerAppId":{"$eq":"app-123"}}' [--receipt-out receipt.json]`

Notes for Benefit Items:
- `benefit-items get`, `list`, `query`, and `count` are reads.
- `benefit-items create`, `update`, `bulk-create`, and `bulk-update` are reviewed-plan writes that only apply live with `--plan-in --apply --yes`.
- `benefit-items delete`, `bulk-delete`, and `bulk-delete-by-filter` are destructive reviewed-plan writes and also require `--ack-irreversible`.
- Official Wix docs say sites using this API must install the Pricing Plans app.
- Reads use Wix app or Wix user identity auth with `SCOPE.BENEFIT_PROGRAMS.READ (PII)`.
- Writes use Wix app or Wix user identity auth with `Manage benefit programs` / `SCOPE.BENEFIT_PROGRAMS.MANAGE`.
- `benefit-items query` defaults to paging limit `50`, and `benefit-items list` retrieves up to `1000` items.
- `benefit-items update` and `bulk-update` require the current `revision`, and verification expects the revision to change after apply.
- Official delete docs warn that removing an item association has immediate effect and may affect active pools.
- Official delete-by-filter behavior could be broad, but this boundary refuses empty-filter bulk delete.

## Read branch metadata

Use these commands to inspect the current Wix branch metadata for a site context.

- `wix-safe-agent-cli branches get-default`
- `wix-safe-agent-cli branches get --branch-id <branch_id>`
- `wix-safe-agent-cli branches query --query-json '{...}'`

Notes for Branches:
- `branches get-default`, `branches get`, and `branches query` are read-only in this boundary.
- These commands use Wix app or Wix user identity auth for the current site context.
- This family uses permission `Manage Site Branches`.
- `branches query` defaults to sort `updatedDate DESC` with `paging.limit 50` and `paging.offset 0` unless the request overrides them.
- Wix says the API manages branch metadata only; editing branch content itself is only possible in the editor.

## Read and manage Contacts V4

These Contacts V4 commands are supported for the current release.

- `wix-safe-agent-cli contacts list [--limit N] [--offset N] [--sort-json '{...}'] [--fields-json '["..."]'] [--fieldsets-json '["..."]']`
- `wix-safe-agent-cli contacts get --contact-id <id> [--fields-json '["..."]'] [--fieldsets-json '["..."]']`
- `wix-safe-agent-cli contacts query [--query-json '{...}'] [--filter-json '{...}'] [--sort-json '{...}'] [--search <text>] [--fields-json '["..."]'] [--limit N] [--offset N]`
- `wix-safe-agent-cli contacts list-facets`
- `wix-safe-agent-cli contacts query-facets --query-json '{...}'`
- `wix-safe-agent-cli contacts get-bulk-job --job-id <job_id>`
- `wix-safe-agent-cli contacts preview-merge --target-contact-id <contact_id> --merge-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts create --contact-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts update --contact-id <contact_id> --contact-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts delete --contact-id <contact_id>`
- `wix-safe-agent-cli --plan-out plan.json contacts merge --target-contact-id <contact_id> --merge-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts label --contact-id <contact_id> --labels-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts unlabel --contact-id <contact_id> --labels-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts bulk-delete --bulk-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts bulk-update --bulk-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contacts bulk-label-unlabel --bulk-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contacts create --contact-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contacts update --contact-id <contact_id> --contact-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contacts delete --contact-id <contact_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contacts merge --target-contact-id <contact_id> --merge-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contacts label --contact-id <contact_id> --labels-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contacts unlabel --contact-id <contact_id> --labels-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contacts bulk-delete --bulk-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contacts bulk-update --bulk-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contacts bulk-label-unlabel --bulk-json '{...}' [--receipt-out receipt.json]`

Notes for Contacts V4:
- `contacts list`, `get`, `query`, `list-facets`, `query-facets`, `get-bulk-job`, and `preview-merge` are read commands in this boundary.
- `contacts preview-merge` performs Wix's dry-run merge preview and does not change contact data.
- `contacts create`, `update`, `label`, and `unlabel` are reviewed-plan writes.
- `contacts update` requires `contact.revision` in `--contact-json`.
- `contacts delete`, `merge`, `bulk-delete`, `bulk-update`, and `bulk-label-unlabel` require `--ack-irreversible`.
- Bulk commands start Wix Contacts bulk jobs; check the returned job with `contacts get-bulk-job`.

## Manage contact labels

- `wix-safe-agent-cli contact-labels query --query-json '{...}'`
- `wix-safe-agent-cli contact-labels list`
- `wix-safe-agent-cli --plan-out plan.json contact-labels find-or-create --label-json '{...}'`
- `wix-safe-agent-cli contact-labels get --key <label_key>`
- `wix-safe-agent-cli --plan-out plan.json contact-labels update --key <label_key> --label-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-labels delete --key <label_key>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-labels find-or-create --label-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-labels update --key <label_key> --label-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contact-labels delete --key <label_key> [--receipt-out receipt.json]`

Notes for Contact Labels:
- `contact-labels query`, `contact-labels list`, and `contact-labels get` are read commands in this boundary.
- These commands use Wix app or Wix user identity auth in this boundary for the target site context.
- This family uses permission `Manage Contact Labels`.
- `find-or-create`, `update`, and `delete` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `find-or-create` is still a write because it can create a new contact label.
- `update` verifies writes by rereading the label after apply.
- `delete` requires `--ack-irreversible`, applies through reviewed plan mode, and verifies success by read-back absence (`404`) for the label key.
- Deleting a label removes it from contacts and triggers label-related events.
- This family is locally proven and live-unverified; proof is based on mocked read/read-back checks and contract-aware test flows.

## Read and manage contact extended fields

- `wix-safe-agent-cli contact-extended-fields get --key <extended_field_key>`
- `wix-safe-agent-cli contact-extended-fields list`
- `wix-safe-agent-cli contact-extended-fields query --query-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-extended-fields find-or-create --field-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-extended-fields update --key <extended_field_key> --field-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-extended-fields delete --key <extended_field_key>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-extended-fields find-or-create --field-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-extended-fields update --key <extended_field_key> --field-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contact-extended-fields delete --key <extended_field_key> [--receipt-out receipt.json]`

Notes for Contact Extended Fields:
- `contact-extended-fields get`, `list`, and `query` are read commands in this boundary.
- `contact-extended-fields find-or-create`, `update`, and `delete` are reviewed-plan writes.
- This family uses permission `Manage Contact Extended Fields`.
- `find-or-create` can create a new custom field if no field with the requested name exists.
- `delete` requires `--ack-irreversible` because Wix says deleting an extended field permanently deletes any contact data stored in that field.

## Read and manage contact notes

- `wix-safe-agent-cli contact-notes get --note-id <note_id>`
- `wix-safe-agent-cli contact-notes query --query-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-notes create --note-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-notes update --note-id <note_id> --note-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-notes delete --note-id <note_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-notes create --note-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-notes update --note-id <note_id> --note-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contact-notes delete --note-id <note_id> [--receipt-out receipt.json]`

Notes for Contact Notes:
- `contact-notes get` and `query` are read commands in this boundary.
- `contact-notes create`, `update`, and `delete` are reviewed-plan writes.
- This family uses `Read Notes` for reads and `Manage Notes` for writes.
- Wix says every note must be associated with an existing contact, note text is limited to 2048 characters, and update requires the current note revision.
- `contact-notes delete` requires `--ack-irreversible` because it removes a contact history note.

## Read and manage contact attachments

- `wix-safe-agent-cli contact-attachments get --contact-id <contact_id> --attachment-id <attachment_id>`
- `wix-safe-agent-cli contact-attachments list --contact-id <contact_id>`
- `wix-safe-agent-cli --plan-out plan.json contact-attachments generate-upload-url --contact-id <contact_id> --attachment-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json contact-attachments delete --contact-id <contact_id> --attachment-id <attachment_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contact-attachments generate-upload-url --contact-id <contact_id> --attachment-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contact-attachments delete --contact-id <contact_id> --attachment-id <attachment_id> [--receipt-out receipt.json]`

Notes for Contact Attachments:
- `contact-attachments get` and `list` are read commands in this boundary.
- `contact-attachments generate-upload-url` and `delete` are reviewed-plan writes.
- This family uses permission `Manage Contact Attachments`.
- Wix says every attachment is associated with a contact ID and the upload URL flow works together with the Upload API.
- `contact-attachments delete` requires `--ack-irreversible` because it removes a saved contact file attachment.

## Read and manage CRM tasks

- `wix-safe-agent-cli crm-tasks get --task-id <task_id>`
- `wix-safe-agent-cli crm-tasks query [--query-json '{...}']`
- `wix-safe-agent-cli crm-tasks count [--filter-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json crm-tasks create --task-json '{"task":{"title":"Call customer"}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-tasks update --task-json '{"task":{"id":"<task_id>","revision":"<revision>","title":"Call customer"}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-tasks move-after --task-id <task_id> [--move-json '{"beforeTaskId":"<before_task_id>"}']`
- `wix-safe-agent-cli --plan-out plan.json crm-tasks delete --task-id <task_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-tasks create --task-json '{"task":{"title":"Call customer"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-tasks update --task-json '{"task":{"id":"<task_id>","revision":"<revision>","title":"Call customer"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-tasks move-after --task-id <task_id> [--move-json '{"beforeTaskId":"<before_task_id>"}'] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json crm-tasks delete --task-id <task_id> [--receipt-out receipt.json]`

Notes for CRM Tasks:
- `crm-tasks get`, `query`, and `count` are read commands in this boundary.
- `crm-tasks create`, `update`, `move-after`, and `delete` are reviewed-plan writes.
- `crm-tasks delete` requires `--ack-irreversible` because it removes a CRM task.
- Wix says `query` defaults to `createdDate DESC`, `count` can accept an optional filter, `update` requires the existing task revision, and `move-after` can place a task first when `beforeTaskId` is omitted.
- Task Created, Task Deleted, Task Overdue, and Task Updated are callback-only events and are not CLI commands.

## Read and manage CRM pipelines

- `wix-safe-agent-cli crm-pipelines get --pipeline-id <pipeline_id>`
- `wix-safe-agent-cli crm-pipelines query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json crm-pipelines create --pipeline-json '{"pipeline":{"name":"Sales","stages":[{"name":"New"}],"doneStage":{"allowedOutcomes":["WON"]}}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-pipelines update --pipeline-json '{"pipeline":{"id":"<pipeline_id>","revision":"<revision>","name":"Sales"}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-pipelines bulk-update-tags --tags-json '{"pipelineIds":["<pipeline_id>"],"assignTags":["hot"]}'`
- `wix-safe-agent-cli --plan-out plan.json crm-pipelines bulk-update-tags-by-filter --tags-json '{"filter":{"name":{"$startsWith":"Sales"}},"assignTags":["hot"]}'`
- `wix-safe-agent-cli --plan-out plan.json crm-pipelines delete --pipeline-id <pipeline_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-pipelines create --pipeline-json '{"pipeline":{"name":"Sales","stages":[{"name":"New"}],"doneStage":{"allowedOutcomes":["WON"]}}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-pipelines update --pipeline-json '{"pipeline":{"id":"<pipeline_id>","revision":"<revision>","name":"Sales"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-pipelines bulk-update-tags --tags-json '{"pipelineIds":["<pipeline_id>"],"assignTags":["hot"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json crm-pipelines bulk-update-tags-by-filter --tags-json '{"filter":{"name":{"$startsWith":"Sales"}},"assignTags":["hot"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json crm-pipelines delete --pipeline-id <pipeline_id> [--receipt-out receipt.json]`

Notes for CRM Pipelines:
- All current callable CRM Pipelines method pages are marked Developer Preview by Wix.
- `crm-pipelines get` and `query` are read commands in this boundary.
- `crm-pipelines create`, `update`, `bulk-update-tags`, `bulk-update-tags-by-filter`, and `delete` are reviewed-plan writes.
- `crm-pipelines delete` requires `--ack-irreversible` because deleting a pipeline permanently removes it from the site.
- `crm-pipelines bulk-update-tags-by-filter` requires `--ack-irreversible` because an omitted filter updates all pipelines and the method returns an async job ID.
- Wix says `create` requires at least one stage plus `doneStage`, `doneStage` must allow at least one outcome, currency cannot be changed once set, and `update` requires the current pipeline revision.
- Pipeline Created, Pipeline Deleted, and Pipeline Updated are callback-only events and are not CLI commands.

## Read and manage CRM cards

- `wix-safe-agent-cli crm-cards get --card-id <card_id>`
- `wix-safe-agent-cli crm-cards query [--query-json '{...}']`
- `wix-safe-agent-cli crm-cards search [--search-json '{...}']`
- `wix-safe-agent-cli crm-cards search-by-stage --search-json '{"pipelineId":"<pipeline_id>","stageId":"<stage_id>"}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards create --card-json '{"card":{"name":"Lead","pipelineId":"<pipeline_id>","stageId":"<stage_id>"}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards update --card-json '{"card":{"id":"<card_id>","revision":"<revision>","name":"Lead"}}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards bulk-update-tags --tags-json '{"cardIds":["<card_id>"],"assignTags":["hot"]}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards bulk-update-tags-by-filter --tags-json '{"pipelineId":"<pipeline_id>","filter":{"name":{"$startsWith":"Lead"}},"assignTags":["hot"]}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards move --card-id <card_id> --move-json '{"stageId":"<stage_id>"}'`
- `wix-safe-agent-cli --plan-out plan.json crm-cards delete --card-id <card_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-cards create --card-json '{"card":{"name":"Lead","pipelineId":"<pipeline_id>","stageId":"<stage_id>"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-cards update --card-json '{"card":{"id":"<card_id>","revision":"<revision>","name":"Lead"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-cards bulk-update-tags --tags-json '{"cardIds":["<card_id>"],"assignTags":["hot"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json crm-cards bulk-update-tags-by-filter --tags-json '{"pipelineId":"<pipeline_id>","filter":{"name":{"$startsWith":"Lead"}},"assignTags":["hot"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json crm-cards move --card-id <card_id> --move-json '{"stageId":"<stage_id>"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json crm-cards delete --card-id <card_id> [--receipt-out receipt.json]`

Notes for CRM Cards:
- All current callable CRM Cards method pages are marked Developer Preview by Wix.
- `crm-cards get`, `query`, `search`, and `search-by-stage` are read commands in this boundary.
- `crm-cards create`, `update`, `bulk-update-tags`, `bulk-update-tags-by-filter`, `move`, and `delete` are reviewed-plan writes.
- `crm-cards delete` requires `--ack-irreversible` because deleting a card permanently removes it from the site.
- `crm-cards bulk-update-tags-by-filter` requires `--ack-irreversible` because an omitted filter updates all cards in the pipeline and the method returns an async job ID.
- Wix says cards must belong to an existing pipeline and stage, can move only between stages in the same pipeline, `update` requires the current card revision, and card `pipelineId` and `currency` cannot be updated.
- Card Assigned, Card Created, Card Deleted, Card Moved, Card Overdue, Card Stale, and Card Updated are callback-only events and are not CLI commands.

## Read and manage AI Site-Chat

- `wix-safe-agent-cli ai-site-chat-widget-settings get`
- `wix-safe-agent-cli --plan-out plan.json ai-site-chat-widget-settings set --settings-json '{"settings":{"enabled":true}}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json ai-site-chat-widget-settings set --settings-json '{"settings":{"enabled":true}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli ai-site-chat-widget-settings-v2 get`
- `wix-safe-agent-cli --plan-out plan.json ai-site-chat-widget-settings-v2 update --settings-json '{"settings":{"enabled":true},"fieldMask":["enabled"]}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json ai-site-chat-widget-settings-v2 update --settings-json '{"settings":{"enabled":true},"fieldMask":["enabled"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli ai-site-chat-conversations get`
- `wix-safe-agent-cli ai-site-chat-messages list [--params-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json ai-site-chat-messages bulk-create --messages-json '{"messages":[{"body":{"text":"Hi"}}]}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json ai-site-chat-messages bulk-create --messages-json '{"messages":[{"body":{"text":"Hi"}}]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli ai-site-chat-messages bulk-get-by-inbox [--params-json '{...}']`
- `wix-safe-agent-cli ai-site-chat-messages media-upload-url`

Notes for AI Site-Chat:
- Wix says the AI Site-Chat app must be installed and is currently only available in the Wix Editor.
- Conversations and visitor-scoped Messages methods must be called with site visitor or site member identity.
- V1 Widget Settings get/set are still callable but deprecated by Wix for October 25, 2026; V2 settings are preferred.
- `ai-site-chat-messages bulk-create` requires `--ack-irreversible` because it sends chat messages.

## Manage CMS data permissions

- `wix-safe-agent-cli data-permissions get --data-collection-id <collection_id>`
- `wix-safe-agent-cli data-permissions get-my --data-collection-id <collection_id>`
- `wix-safe-agent-cli --plan-out plan.json data-permissions update --data-collection-id <collection_id> --item-read ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-insert ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-update ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-remove ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED`
- `wix-safe-agent-cli --plan-out plan.json data-permissions add-special --data-collection-id <collection_id> [--user-id <user_id> | --policy-id <policy_id>] --item-read ALLOWED|UNSPECIFIED --item-insert ALLOWED|UNSPECIFIED --item-update ALLOWED|UNSPECIFIED --item-remove ALLOWED|UNSPECIFIED`
- `wix-safe-agent-cli --plan-out plan.json data-permissions update-special --data-collection-id <collection_id> --special-permissions-id <special_permissions_id> [--user-id <user_id> | --policy-id <policy_id>] --item-read ALLOWED|UNSPECIFIED --item-insert ALLOWED|UNSPECIFIED --item-update ALLOWED|UNSPECIFIED --item-remove ALLOWED|UNSPECIFIED`
- `wix-safe-agent-cli --plan-out plan.json data-permissions remove-special --data-collection-id <collection_id> --special-permissions-id <special_permissions_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-permissions update --data-collection-id <collection_id> --item-read ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-insert ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-update ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED --item-remove ANYONE|SITE_MEMBER|SITE_MEMBER_AUTHOR|CMS_EDITOR|PRIVILEGED [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-permissions add-special --data-collection-id <collection_id> [--user-id <user_id> | --policy-id <policy_id>] --item-read ALLOWED|UNSPECIFIED --item-insert ALLOWED|UNSPECIFIED --item-update ALLOWED|UNSPECIFIED --item-remove ALLOWED|UNSPECIFIED [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-permissions update-special --data-collection-id <collection_id> --special-permissions-id <special_permissions_id> [--user-id <user_id> | --policy-id <policy_id>] --item-read ALLOWED|UNSPECIFIED --item-insert ALLOWED|UNSPECIFIED --item-update ALLOWED|UNSPECIFIED --item-remove ALLOWED|UNSPECIFIED [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-permissions remove-special --data-collection-id <collection_id> --special-permissions-id <special_permissions_id> [--receipt-out receipt.json]`

Notes for Data Permissions:
- `data-permissions get` and `data-permissions get-my` are read commands in this boundary.
- `data-permissions update`, `add-special`, `update-special`, and `remove-special` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- This family uses Wix app or Wix user identity auth in this boundary for the target site context.
- This family uses permission `Manage Data Collections`.
- Official Wix docs say this family applies only to collections created in the CMS or through the Data Collections API. Wix app collections, shared collections, and external collections are outside this family.
- Collection-level access values in this tool are `ANYONE`, `SITE_MEMBER`, `SITE_MEMBER_AUTHOR`, `CMS_EDITOR`, and `PRIVILEGED`.
- `add-special` and `update-special` require exactly one identity selector: `--user-id` or `--policy-id`.
- `update-special` requires all four access flags every time because the official method is replace-style and omitted fields become `UNSPECIFIED`.
- `update-special` and `remove-special` require `--data-collection-id` in this tool so apply can reread the collection permissions and prove the result instead of trusting the write response alone.
- These writes keep the saved before-state snapshot explicit and do not promise automatic rollback.
- This family is locally proven and live-unverified; proof is based on mocked read/read-back checks and reviewed-plan contract tests.

## Read CMS Wix app collections

Wix app collections do not have a separate REST command family in this tool. Use the shipped CMS read commands with the official app collection IDs and field rules.

- `wix-safe-agent-cli data-collections list`
- `wix-safe-agent-cli data-collections get --data-collection-id <app_collection_id>`
- `wix-safe-agent-cli data-collections get --data-collection-id Stores/Products`
- `wix-safe-agent-cli data-collections get --data-collection-id Bookings/Services`
- `wix-safe-agent-cli data-items query --data-collection-id <app_collection_id> --query-json @query.json`
- `wix-safe-agent-cli data-items query --data-collection-id Events/Events --query-json @query.json`
- `wix-safe-agent-cli data-items search --data-collection-id <app_collection_id> --search-json @search.json`

Notes for Wix app collections:
- Official Wix docs say app collections are system collections automatically created and managed by Wix business apps.
- Official Wix docs say app collections are accessed with the same tools used for other CMS collections, such as Wix Data APIs.
- Official Wix docs say these collections have fixed permissions and read-only fields that must be changed from the relevant app dashboard or app API, not through CMS collection writes.
- Check the specific app collection reference page before filtering or selecting fields, because each collection documents its own IDs and filterable fields.

## Manage CMS data sharing

- `wix-safe-agent-cli data-sharing list-policies [--data-collection-ids-json '["collectionId"]']`
- `wix-safe-agent-cli data-sharing get-policy --policy-id <policy_id>`
- `wix-safe-agent-cli data-sharing list-shared-collections [--shared-with-current-site]`
- `wix-safe-agent-cli --plan-out plan.json data-sharing create-policy --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json data-sharing update-policy --policy-id <policy_id> --policy-json @policy.json`
- `wix-safe-agent-cli --plan-out plan.json data-sharing delete-policy --policy-id <policy_id>`
- `wix-safe-agent-cli --plan-out plan.json data-sharing connect --connection-json @connection.json`
- `wix-safe-agent-cli --plan-out plan.json data-sharing disconnect --connection-json @connection.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-sharing create-policy --policy-json @policy.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-sharing update-policy --policy-id <policy_id> --policy-json @policy.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-sharing delete-policy --policy-id <policy_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-sharing connect --connection-json @connection.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-sharing disconnect --connection-json @connection.json [--receipt-out receipt.json]`

Notes for Data Sharing:
- `data-sharing list-policies`, `get-policy`, and `list-shared-collections` are read commands.
- `data-sharing create-policy`, `update-policy`, and `connect` are reviewed-plan writes.
- `data-sharing delete-policy` and `disconnect` are reviewed-plan writes that also require `--ack-irreversible`.
- Official Wix docs say deleting a sharing policy disconnects all associated connections, and target sites immediately lose access to the collection and its data.
- Official Wix docs say disconnecting removes the current site's local view of the shared collection; it does not affect the source site or other target sites.
- Official Wix docs say Data Sharing only works between sites in the same Wix account, external collections and Wix App collections cannot be shared, and collection permissions remain unchanged when shared.
- Official Wix docs say `update-policy` can only update `dataItemsFilter`, and updates automatically apply to all connected sites.
- This family uses permission `Manage Data Collection Sharing` and remains live-unverified.

## Manage CMS data indexes

- `wix-safe-agent-cli data-indexes list --data-collection-id <collection_id> [--limit N] [--offset N]`
- `wix-safe-agent-cli --plan-out plan.json data-indexes create --data-collection-id <collection_id> --index-json '{"name":"slug","fields":[{"path":"slug","order":"ASC"}]}'`
- `wix-safe-agent-cli --plan-out plan.json data-indexes drop --data-collection-id <collection_id> --index-name <index_name>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-indexes create --data-collection-id <collection_id> --index-json '{"name":"slug","fields":[{"path":"slug","order":"ASC"}]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-indexes drop --data-collection-id <collection_id> --index-name <index_name> [--receipt-out receipt.json]`

Notes for Data Indexes:
- `data-indexes list` is a read command in this boundary.
- `data-indexes create` and `drop` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- This family uses Wix app or Wix user identity auth in this boundary for the target site context.
- This family uses permission `Manage Data Indexes`.
- Official Wix docs say Wix Data APIs require the site code editor to be enabled.
- `list` uses the official `dataCollectionId` query plus optional paging limit and offset.
- `create` uses explicit `--index-json` because the official create request includes a nested index object with name, fields, and optional `unique` / `caseInsensitive`.
- This tool rejects obviously invalid create shapes locally, including empty fields, more than 3 fields, and unique indexes with more than 1 field.
- `create` and `drop` are async state changes. This tool verifies them by rereading the index list and checking statuses like `BUILDING`, `ACTIVE`, `DROPPING`, and `DROPPED`.
- This tool refuses dropping `SYSTEM` indexes when readback proves the index is system-generated.
- Official Wix docs say failed index creation still occupies a slot until the failed index is dropped.
- This family is locally proven and live-unverified; proof is based on mocked read/read-back checks and reviewed-plan contract tests.

## Manage CMS collection folders

- `wix-safe-agent-cli data-folders get [--folder-id <folder_id>]`
- `wix-safe-agent-cli --plan-out plan.json data-folders create --name "<folder_name>" [--description "<description>"]`
- `wix-safe-agent-cli --plan-out plan.json data-folders update --folder-id <folder_id> [--name "<folder_name>"] [--description "<description>"]`
- `wix-safe-agent-cli --plan-out plan.json data-folders delete --folder-id <folder_id>`
- `wix-safe-agent-cli --plan-out plan.json data-folders create-collection-reference --collection-name "<collection_name>" [--folder-id <folder_id>]`
- `wix-safe-agent-cli data-folders get-collection-references --collection-name "<collection_name>"`
- `wix-safe-agent-cli --plan-out plan.json data-folders delete-collection-reference --collection-name "<collection_name>" [--folder-id <folder_id>]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-folders create --name "<folder_name>" [--description "<description>"] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-folders update --folder-id <folder_id> [--name "<folder_name>"] [--description "<description>"] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-folders delete --folder-id <folder_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-folders create-collection-reference --collection-name "<collection_name>" [--folder-id <folder_id>] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-folders delete-collection-reference --collection-name "<collection_name>" [--folder-id <folder_id>] [--receipt-out receipt.json]`

Notes for Data Folders:
- `data-folders get` is a read command in this boundary. Omitting `--folder-id` returns the root folder.
- `data-folders create`, `update`, `delete`, `create-collection-reference`, and `delete-collection-reference` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `data-folders delete` also requires `--ack-irreversible`.
- This family uses Wix app or Wix user identity auth in this boundary for the target site context.
- This family uses permission `Manage Data Collections`.
- Official Wix docs say only the root folder may contain other folders.
- Official Wix docs also say the root folder cannot be updated or deleted.
- `get-collection-references` is a read-only helper that returns all folder references for one collection name.
- `create-collection-reference` and `delete-collection-reference` verify by rereading the collection references after apply.
- `delete` verifies by rereading the folder ID and expecting `404`. Collection references move back to the root folder when a folder is deleted.
- This family is locally proven and live-unverified; proof is based on mocked read/read-back checks and reviewed-plan contract tests.

## Manage data extension schemas

- `wix-safe-agent-cli data-extension-schemas list --fqdn <fqdn> [--namespaces-json '["..."]'] [--fields-json '["..."]'] [--extension-points-json '["..."]']`
- `wix-safe-agent-cli --plan-out plan.json data-extension-schemas create --data-extension-schema-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json data-extension-schemas update --data-extension-schema-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json data-extension-schemas delete-user-defined-fields --data-extension-schema-id <schema_id> --fqdn <fqdn> --fields-to-delete-json '["..."]'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-extension-schemas create --data-extension-schema-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-extension-schemas update --data-extension-schema-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-extension-schemas delete-user-defined-fields --data-extension-schema-id <schema_id> --fqdn <fqdn> --fields-to-delete-json '["..."]' [--receipt-out receipt.json]`

Notes for Data Extension Schemas:
- `data-extension-schemas list` is a read command in this boundary and needs an explicit FQDN for the object being extended.
- `data-extension-schemas create`, `update`, and `delete-user-defined-fields` are reviewed-plan writes with `--plan-out` then `--plan-in --apply --yes`.
- `data-extension-schemas delete-user-defined-fields` also requires `--ack-irreversible`.
- This family uses Wix app or Wix user identity auth in this boundary for the target site context.
- The API manages user-defined schema content for a target FQDN. The surrounding schema-plugin extension still starts in the app dashboard and is released through app versioning.
- `create` and `update` verify by rereading the schema list for the same FQDN.
- `delete-user-defined-fields` verifies by rereading the schema list and checking that the requested field paths are gone.
- This family is locally proven in unit tests only and still needs live Wix proof.

## Manage members

These member-management methods are available as explicit named commands. Reads inspect members; writes always use a reviewed plan before live apply.

- `wix-safe-agent-cli members list [--limit N] [--offset N] [--sort-json '{...}'] [--fieldsets-json '["..."]']`
- `wix-safe-agent-cli members get --member-id <id> [--fieldsets-json '["..."]']`
- `wix-safe-agent-cli members query [--query-json '{...}'] [--fieldsets-json '["..."]']`
- `wix-safe-agent-cli members get-my`
- `wix-safe-agent-cli --plan-out plan.json members create --member-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json members update --member-id <id> --member-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json members delete --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members delete-my [--delete-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json members bulk-delete --member-ids-json '["member_id"]'`
- `wix-safe-agent-cli --plan-out plan.json members approve --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members block --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members mute --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members unmute --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members disconnect --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members delete-addresses --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members delete-emails --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members delete-phones --member-id <id>`
- `wix-safe-agent-cli --plan-out plan.json members bulk-approve --filter-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json members bulk-block --filter-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json members bulk-delete-by-filter --filter-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json members join-community`
- `wix-safe-agent-cli --plan-out plan.json members leave-community`
- `wix-safe-agent-cli --plan-out plan.json members update-member-slug --member-id <id> --slug <slug>`
- `wix-safe-agent-cli --plan-out plan.json members update-my-slug --slug <slug>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members create --member-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members update --member-id <id> --member-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members delete --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members delete-my [--delete-json '{...}'] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members bulk-delete --member-ids-json '["member_id"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members approve --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members block --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members mute --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members unmute --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members disconnect --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members delete-addresses --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members delete-emails --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members delete-phones --member-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members bulk-approve --filter-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members bulk-block --filter-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members bulk-delete-by-filter --filter-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members join-community [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members leave-community [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members update-member-slug --member-id <id> --slug <slug> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members update-my-slug --slug <slug> [--receipt-out receipt.json]`

Notes for Members:
- `members list`, `get`, `query`, and `get-my` are read commands.
- `members create`, `update`, `approve`, `block`, `mute`, `unmute`, bulk approve/block, community join/leave, and slug updates are reviewed-plan writes.
- `members delete`, `delete-my`, `bulk-delete`, `bulk-delete-by-filter`, `disconnect`, `delete-addresses`, `delete-emails`, and `delete-phones` also require `--ack-irreversible`.
- Official Wix docs say current-member methods require visitor or member authentication. The CLI can only succeed when the supplied token has that valid identity context.
- Official Wix docs say `create` calls should be spaced at least one second apart when creating multiple members.
- Official Wix docs say `update` cannot update `privacyStatus` or `loginEmail`, and empty `contact.addresses`, `contact.emails`, or `contact.phones` arrays do not clear those arrays. Use `delete-addresses`, `delete-emails`, or `delete-phones` to clear them.
- Official Wix docs say deleting members transfers created content to another account, and disconnecting a member is irreversible.
- Member Created, Member Deleted, and Member Updated are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Manage member activity counters

Activity counters track member activity metrics across Wix apps.

- `wix-safe-agent-cli activity-counters get --member-id <member_id>`
- `wix-safe-agent-cli activity-counters query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json activity-counters set --member-id <member_id> --activity-counters-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json activity-counters set --member-id <member_id> --activity-counters-json '{...}' [--receipt-out receipt.json]`

Notes for Activity Counters:
- `activity-counters get` and `query` are read commands.
- `activity-counters set` is a reviewed-plan write that creates or updates counters for the requested member.
- Official Wix docs say callers must pass a member ID, not a contact ID.
- Official Wix docs say public counters can be read more broadly, while private counters are visible only to the counter owner and the relevant member.
- Official Wix docs say there is currently no way to retrieve all private and public counters at the app level.
- Activity Counter Updated is a webhook event, so this CLI records it in inventory but does not expose a command for it.

## Manage member badges

Badges V4 manages badge definitions shown on member profiles. Assigning badges to members is handled by the separate Badge Assignments API.

- `wix-safe-agent-cli badges-v4 get --badge-id <badge_id>`
- `wix-safe-agent-cli badges-v4 query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json badges-v4 create --badge-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badges-v4 create --badge-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badges-v4 update --badge-id <badge_id> --badge-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badges-v4 update --badge-id <badge_id> --badge-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badges-v4 move --badge-id <badge_id> --move-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badges-v4 move --badge-id <badge_id> --move-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badges-v4 delete --badge-id <badge_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json badges-v4 delete --badge-id <badge_id> [--receipt-out receipt.json]`

Notes for Badges V4:
- `badges-v4 get` and `query` are read commands.
- `badges-v4 create`, `update`, and `move` are reviewed-plan writes.
- `badges-v4 delete` is a reviewed-plan write and also requires `--ack-irreversible`.
- Official Wix docs say deleting a badge removes it from all assigned members.
- Official Wix docs mark the older Update Badges Display Order method as deprecated and replaced by Move Badge, so this CLI exposes `badges-v4 move` instead.
- Badge Created, Badge Updated, and Badge Deleted are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Manage member badge assignments

Badge Assignments connect existing Badges V4 definitions to members. The site must have Wix Members Area installed.

- `wix-safe-agent-cli badge-assignments query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments create --assignment-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badge-assignments create --assignment-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments bulk-create --assignments-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badge-assignments bulk-create --assignments-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments bulk-update-tags --tags-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json badge-assignments bulk-update-tags --tags-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments delete --assignment-id <assignment_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json badge-assignments delete --assignment-id <assignment_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments bulk-delete --delete-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json badge-assignments bulk-delete --delete-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json badge-assignments bulk-update-tags-by-filter --filter-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json badge-assignments bulk-update-tags-by-filter --filter-json '{...}' [--receipt-out receipt.json]`

Notes for Badge Assignments:
- `badge-assignments query` is a read command.
- `badge-assignments create`, `bulk-create`, and `bulk-update-tags` are reviewed-plan writes.
- `badge-assignments delete` and `bulk-delete` are reviewed-plan writes and also require `--ack-irreversible`.
- `badge-assignments bulk-update-tags-by-filter` is a reviewed-plan write and also requires `--ack-irreversible` because an empty filter can update all matching assignments asynchronously.
- Official Wix docs say deleting a badge assignment removes associated permissions or privileges from the member and cannot be undone.
- Badge Assignment Created and Badge Assignment Deleted are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Manage member reports

Member Reports lets members or site flows report inappropriate behavior such as spam, hate speech, or harassment. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-reports query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json member-reports report --report-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-reports report --report-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-reports delete --member-id <member_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json member-reports delete --member-id <member_id> [--receipt-out receipt.json]`

Notes for Member Reports:
- `member-reports query` is a read command.
- `member-reports report` is a reviewed-plan write that creates a moderation report and can notify the Wix user by email.
- `member-reports delete` is a reviewed-plan write and also requires `--ack-irreversible` because it deletes all reports for the requested member.
- Official Wix docs say query defaults to `createdDate ASC`, `paging.limit` `100`, and `paging.offset` `0`.
- Member Report Created and Member Report Deleted are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Manage member follow connections

Members Followers lets site members follow and unfollow each other. The site must have Wix Members Area installed.

- `wix-safe-agent-cli members-followers list-followers --member-id <member_id>`
- `wix-safe-agent-cli members-followers list-following --member-id <member_id>`
- `wix-safe-agent-cli members-followers list-my-followers`
- `wix-safe-agent-cli members-followers list-my-following`
- `wix-safe-agent-cli members-followers query-connections --member-id <member_id> [--query-json '{...}']`
- `wix-safe-agent-cli members-followers query-my-connections [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json members-followers follow --member-id <member_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json members-followers follow --member-id <member_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json members-followers unfollow --member-id <member_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json members-followers unfollow --member-id <member_id> [--receipt-out receipt.json]`

Notes for Members Followers:
- List and query commands are reads.
- `members-followers follow` is a reviewed-plan write that makes the current member follow another member.
- `members-followers unfollow` is a reviewed-plan write and also requires `--ack-irreversible`.
- Official Wix docs say `query-connections` returns no data when `connectedMemberIds` is an empty array.
- Member Followed and Follow Member Unfollowed are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Query user members

User Member lets you read members that are also Wix users. The site must have Wix Members Area installed.

- `wix-safe-agent-cli user-members query [--query-json '{...}']`

Notes for User Member:
- `user-members query` is a read-only POST query.
- Official Wix docs say it can use visitor/member authentication or account-level API key auth.
- Official Wix docs say query defaults to `createdDate ASC`, `paging.limit` `100`, and `paging.offset` `0`.

## Send member set-password emails

Member Authentication lets you send a site member an email with a one-time link to set or reset their password.

- `wix-safe-agent-cli --plan-out plan.json member-authentication send-set-password-email --email-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json member-authentication send-set-password-email --email-json '{...}' [--receipt-out receipt.json]`

Notes for Member Authentication:
- `member-authentication send-set-password-email` is a reviewed-plan write.
- It also requires `--ack-irreversible` because the email cannot be unsent.
- Official Wix docs mark this method Developer Preview.
- Official Wix docs say the set-password link is valid for 3 hours and can be used only once.
- A receipt proves Wix accepted the request, not that the email reached the inbox.

## Manage member About sections

Members About V2 lets you read and manage the rich-content "About" section on member profiles. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-abouts get --about-id <about_id>`
- `wix-safe-agent-cli member-abouts query [--query-json '{...}']`
- `wix-safe-agent-cli member-abouts get-my`
- `wix-safe-agent-cli --plan-out plan.json member-abouts create --about-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-abouts create --about-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-abouts update --about-id <about_id> --about-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-abouts update --about-id <about_id> --about-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-abouts delete --about-id <about_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json member-abouts delete --about-id <about_id> [--receipt-out receipt.json]`

Notes for Members About V2:
- `member-abouts get`, `query`, and `get-my` are reads.
- `member-abouts create` and `update` are reviewed-plan writes.
- `member-abouts update` requires `memberAbout.revision` in `--about-json`.
- `member-abouts delete` is a reviewed-plan write and also requires `--ack-irreversible`.
- Member About Created, Deleted, and Updated are webhook events, so this CLI records them in inventory but does not expose commands for them.

## Manage member privacy settings

Member Privacy covers the default privacy status for new members and the privacy settings override for current members. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-privacy get-default`
- `wix-safe-agent-cli member-privacy get-settings`
- `wix-safe-agent-cli --plan-out plan.json member-privacy set-default --privacy-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-privacy set-default --privacy-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-privacy set-settings --settings-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-privacy set-settings --settings-json '{...}' [--receipt-out receipt.json]`

Notes for Member Privacy:
- `member-privacy get-default` and `get-settings` are reads.
- `member-privacy set-default` is a reviewed-plan write and official docs mark it Developer Preview.
- `member-privacy set-settings` is a reviewed-plan write and requires `memberPrivacySettings.revision` in `--settings-json`.
- Member privacy settings can affect all current members.

## Manage member custom fields

Member Custom Fields lets you read and manage custom profile fields shown for members. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-custom-fields get --field-id <field_id>`
- `wix-safe-agent-cli member-custom-fields list`
- `wix-safe-agent-cli --plan-out plan.json member-custom-fields create --field-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-fields create --field-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-fields update --field-id <field_id> --field-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-fields update --field-id <field_id> --field-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-fields delete --field-id <field_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json member-custom-fields delete --field-id <field_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-fields hide --field-id <field_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-fields hide --field-id <field_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-fields update-order --order-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-fields update-order --order-json '{...}' [--receipt-out receipt.json]`

Notes for Member Custom Fields:
- `member-custom-fields get` and `list` are reads.
- `member-custom-fields create`, `update`, `hide`, and `update-order` are reviewed-plan writes.
- `member-custom-fields delete` is a reviewed-plan write and also requires `--ack-irreversible`.
- This family remains live-unverified; receipts use the provider response as proof.

## Manage member custom field applications

Member Custom Field Applications lets you restrict which members, roles, badges, or pricing-plan holders a custom field applies to. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-custom-field-applications get --custom-field-id <custom_field_id>`
- `wix-safe-agent-cli member-custom-field-applications list-applications [--applications-json '{...}']`
- `wix-safe-agent-cli member-custom-field-applications get-members --members-json '{...}'`
- `wix-safe-agent-cli member-custom-field-applications get-roles --roles-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json member-custom-field-applications create --application-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-field-applications create --application-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-field-applications update --custom-field-id <custom_field_id> --application-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json member-custom-field-applications update --custom-field-id <custom_field_id> --application-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json member-custom-field-applications delete --custom-field-id <custom_field_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json member-custom-field-applications delete --custom-field-id <custom_field_id> [--receipt-out receipt.json]`

Notes for Member Custom Field Applications:
- `member-custom-field-applications get`, `list-applications`, `get-members`, and `get-roles` are reads.
- `member-custom-field-applications create` and `update` are reviewed-plan writes.
- Official docs say `update` does not support partial updates; pass the whole `application` object.
- `member-custom-field-applications delete` is a reviewed-plan write and also requires `--ack-irreversible` because deleting an application makes the field apply to all members.
- This family remains live-unverified; receipts use the provider response as proof.

## Read member custom field suggestions

Member Custom Field Suggestions lets you inspect custom and system fields suggested for member profiles. The site must have Wix Members Area installed.

- `wix-safe-agent-cli member-custom-field-suggestions query [--query-json '{...}']`
- `wix-safe-agent-cli member-custom-field-suggestions list`

Notes for Member Custom Field Suggestions:
- `member-custom-field-suggestions query` is a read-only POST query.
- `member-custom-field-suggestions list` is a read, and official docs mark it Developer Preview.
- Official docs say `query` defaults to `createdDate ASC`, `paging.limit` `100`, and `paging.offset` `0`.
- This family remains live-unverified.

## Read app installations

- `wix-safe-agent-cli app-installations query [--query-json '{...}'] [--filter-json '{...}'] [--sort-json '{...}'] [--fields-json '["..."]'] [--cursor <cursor>] [--limit N]`
- `wix-safe-agent-cli app-installations search --search <expression> [--search-json '{...}'] [--fields-json '["..."]'] [--cursor <cursor>] [--limit N]`

## App installation state

- `wix-safe-agent-cli app-installation get-installed`
- `wix-safe-agent-cli app-installation is-permitted --request-json '{...}'`

Notes for App Installation state:
- `get-installed` returns the apps installed on the current site context.
- Returned `appToken` values are redacted in command output and receipts.
- `is-permitted` is a preflight check only. It does not change the tenant.

## Manage app installations

- `wix-safe-agent-cli --plan-out plan.json app-installation install --tenant-json '{...}' --app-def-id <app_def_id> [--enabled true|false] [--version <version>]`
- `wix-safe-agent-cli --plan-out plan.json app-installation install-from-share-url --tenant-json '{...}' --share-url-id <share_url_id> [--dev-override-id <dev_override_id>]`
- `wix-safe-agent-cli --plan-out plan.json app-installation uninstall --tenant-json '{...}' --app-def-id <app_def_id>`
- `wix-safe-agent-cli --plan-out plan.json app-installation bulk-install --tenant-json '{...}' --app-instances-json '[...]'`
- `wix-safe-agent-cli --plan-out plan.json app-installation bulk-uninstall --tenant-json '{...}' --app-def-ids-json '[...]'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json app-installation install --tenant-json '{...}' --app-def-id <app_def_id> [--enabled true|false] [--version <version>] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json app-installation install-from-share-url --tenant-json '{...}' --share-url-id <share_url_id> [--dev-override-id <dev_override_id>] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json app-installation uninstall --tenant-json '{...}' --app-def-id <app_def_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json app-installation bulk-install --tenant-json '{...}' --app-instances-json '[...]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json app-installation bulk-uninstall --tenant-json '{...}' --app-def-ids-json '[...]' [--receipt-out receipt.json]`

Notes for App Installation:
- `app-installation install`, `install-from-share-url`, `uninstall`, `bulk-install`, and `bulk-uninstall` are reviewed-plan writes.
- Before-state snapshots are not guaranteed for arbitrary tenant context, so recovery may be manual.
- The official pages say only logged-in Wix users or API key admins can use this API, so this boundary keeps the existing app/user token path and stays live-unverified.
- The App Installation pages show `Manage SEO Settings` on the installed-app read page and `Manage Events` on the install/uninstall pages, so this boundary keeps that docs mismatch explicit.
- `bulk-install` and `bulk-uninstall` accept up to 20 items each in this tool.

## Read app instance

- `wix-safe-agent-cli app-instance get`

Notes for App Instance:
- `app-instance get` uses app-token auth in this boundary.
- This is read-only and calls `GET /apps/v1/instance`.
- This command is the official entry point for current app installation context used by this boundary.

## Manage app permissions

- `wix-safe-agent-cli app-permissions list --app-id <app_id> [--cursor <cursor>] [--limit <n>] [--consistent true|false]`
- `wix-safe-agent-cli --plan-out plan.json app-permissions create --app-id <app_id> --permission-id <permission_id> [--app-permission-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json app-permissions delete --app-id <app_id> --permission-id <permission_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json app-permissions create --app-id <app_id> --permission-id <permission_id> [--app-permission-json '{...}'] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json app-permissions delete --app-id <app_id> --permission-id <permission_id> [--receipt-out receipt.json]`

Notes for App Permissions:
- `app-permissions list` is a read-only command and follows the shipped app/user-token command path.
- `app-permissions create` and `app-permissions delete` are reviewed-plan writes with plan-first flow: `--plan-out`, then `--plan-in --apply --yes`.
- `app-permissions create` and `app-permissions delete` are executed in this boundary through account API-key auth (`Authorization` + `wix-account-id`).
- In this tool, the request path for all three methods is `"/apps/v1/app-permissions/v1/app-permissions"` in `url`.
- Wix official docs are currently inconsistent for this family: all three method pages render the same endpoint and mixed auth text, so this family is implemented but live-unverified.

## Form Schemas

- `wix-safe-agent-cli form-schemas list [--namespace <namespace>] [--limit N] [--offset N]`
- `wix-safe-agent-cli form-schemas get --form-id <form_id>`
- `wix-safe-agent-cli form-schemas query --query-json '{...}'`
- `wix-safe-agent-cli form-schemas count --filter-json '{...}'`
- `wix-safe-agent-cli form-schemas get-deleted --form-id <form_id>`
- `wix-safe-agent-cli form-schemas list-deleted [--namespace <namespace>] [--limit N] [--offset N]`
- `wix-safe-agent-cli form-schemas query-deleted --query-json '{...}'`
- `wix-safe-agent-cli form-schemas count-deleted --filter-json '{...}'`
- `wix-safe-agent-cli form-schemas list-providers-configs`
- `wix-safe-agent-cli form-schemas get-summary --form-id <form_id>`
- `wix-safe-agent-cli --plan-out plan.json form-schemas create --form-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json form-schemas bulk-create --bulk-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json form-schemas update --form-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json form-schemas clone --form-id <form_id> [--clone-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json form-schemas bulk-clone --bulk-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json form-schemas delete --form-id <form_id>`
- `wix-safe-agent-cli --plan-out plan.json form-schemas bulk-delete --bulk-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json form-schemas restore --form-id <form_id>`
- `wix-safe-agent-cli --plan-out plan.json form-schemas remove-from-trash --form-id <form_id>`
- `wix-safe-agent-cli --plan-out plan.json form-schemas bulk-remove-deleted-field --bulk-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json form-schemas create --form-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json form-schemas delete --form-id <form_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json form-schemas remove-from-trash --form-id <form_id> [--receipt-out receipt.json]`

Notes for Form Schemas:
- Read and query commands run directly. Query methods require the official namespace equality filter.
- Create, update, clone, restore, and bulk create/clone are reviewed-plan writes.
- Delete, bulk delete, permanent trash removal, and deleted-field removal require `--ack-irreversible`.
- `form-schemas update` requires `form.id` in `--form-json`.

## Chat Settings

- `wix-safe-agent-cli chat-settings get --chat-settings-id <form_id>`
- `wix-safe-agent-cli chat-settings query --query-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json chat-settings create --chat-settings-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json chat-settings update --chat-settings-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json chat-settings delete --chat-settings-id <form_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json chat-settings create --chat-settings-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json chat-settings update --chat-settings-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json chat-settings delete --chat-settings-id <form_id> [--receipt-out receipt.json]`

Notes for Chat Settings:
- `chat-settings get` and `query` are read commands for Wix Forms AI chat settings.
- `chat-settings create` and `update` are reviewed-plan writes.
- `chat-settings delete` also requires `--ack-irreversible` because it removes the AI chat settings entity for the form.
- Official Wix docs say the Wix Forms app must be installed, each form has exactly one chat settings entity, and the chat settings ID matches the form ID.
- Official Wix docs list the `Manage Intake Form (PII)` permission for Chat Settings methods.
- `chat-settings update` requires `chatSettings.id` and the current `chatSettings.revision` in `--chat-settings-json`.
- Query defaults to `id ASC` with `cursorPaging.limit` 100 unless the request overrides it.

## Interactive Form Sessions

- `wix-safe-agent-cli --plan-out plan.json interactive-form-sessions create --session-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json interactive-form-sessions create-streamed --session-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json interactive-form-sessions send-message --session-id <session_id> --message-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json interactive-form-sessions send-message-streamed --session-id <session_id> --message-json '{...}'`
- `wix-safe-agent-cli interactive-form-sessions generate-summary --form-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json interactive-form-sessions create --session-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json interactive-form-sessions create-streamed --session-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json interactive-form-sessions send-message --session-id <session_id> --message-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json interactive-form-sessions send-message-streamed --session-id <session_id> --message-json '{...}' [--receipt-out receipt.json]`

Notes for Interactive Form Sessions:
- All Interactive Form Sessions methods are marked Developer Preview in official Wix docs.
- Create and send-message commands are reviewed-plan writes because they run an AI conversational form session and can submit extracted form data when the official `dryRun` body field is false.
- `generate-summary` is a non-mutating helper that returns an AI summary of a form, up to 255 characters in official docs.
- The streamed commands send the official `Accept: text/event-stream` header and return normal JSON when Wix responds with JSON, or `rawText` when Wix returns event-stream text.
- Official Wix docs say the commands use `Manage form submissions` / `SCOPE.FORMS.MANAGE-SUBMISSIONS`, with specific permissions for creating sessions and sending messages.
- `send-message` and `send-message-streamed` validate that `input` is present and no longer than the official 10,000-character limit.

## Intake Forms

- `wix-safe-agent-cli intake-forms query [--query-json '{...}']`
- `wix-safe-agent-cli intake-forms create-customer-submission-link --intake-form-id <intake_form_id> [--contact-id <contact_id>]`
- `wix-safe-agent-cli --plan-out plan.json intake-forms archive --intake-form-id <intake_form_id>`
- `wix-safe-agent-cli --plan-out plan.json intake-forms unarchive --intake-form-id <intake_form_id>`
- `wix-safe-agent-cli --plan-out plan.json intake-forms update-expiration-period --intake-form-id <intake_form_id> --expiration-period-in-months 6`
- `wix-safe-agent-cli --plan-out plan.json intake-forms delete --intake-form-id <intake_form_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json intake-forms archive --intake-form-id <intake_form_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json intake-forms unarchive --intake-form-id <intake_form_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json intake-forms update-expiration-period --intake-form-id <intake_form_id> --expiration-period-in-months 6 [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json intake-forms delete --intake-form-id <intake_form_id> [--receipt-out receipt.json]`

Notes for Intake Forms:
- `query` and `create-customer-submission-link` are reads/helpers. The link is valid for 72 hours in official Wix docs and can include an optional `contactId`.
- `archive`, `unarchive`, and `update-expiration-period` are reviewed-plan writes.
- `update-expiration-period` accepts 1 to 60 months and Wix recalculates existing submission expiration dates.
- `delete` requires `--ack-irreversible` because official docs say it deletes the underlying Wix form and orphaned submissions are not returned by Intake Form Submissions methods.
- Official Wix docs say these methods use `Read Intake Form` / `SCOPE.INTAKE-FORM.READ` for reads and `Manage Intake Form (PII)` / `SCOPE.INTAKE-FORM.MANAGE_LIMITED` for writes.

## Intake Form Submissions

- `wix-safe-agent-cli intake-form-submissions query [--query-json '{...}']`
- `wix-safe-agent-cli intake-form-submissions search [--search-json '{...}']`
- `wix-safe-agent-cli intake-form-submissions count-by-intake-form-ids --request-json '{...}'`
- `wix-safe-agent-cli intake-form-submissions list-data-by-contacts --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json intake-form-submissions cancel --submission-id <submission_id>`
- `wix-safe-agent-cli --plan-out plan.json intake-form-submissions extend --submission-id <submission_id>`
- `wix-safe-agent-cli --plan-out plan.json intake-form-submissions exempt --intake-form-id <intake_form_id> --exemption-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json intake-form-submissions delete --submission-id <submission_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json intake-form-submissions cancel --submission-id <submission_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json intake-form-submissions extend --submission-id <submission_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json intake-form-submissions exempt --intake-form-id <intake_form_id> --exemption-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json intake-form-submissions delete --submission-id <submission_id> [--receipt-out receipt.json]`

Notes for Intake Form Submissions:
- `query`, `search`, `count-by-intake-form-ids`, and `list-data-by-contacts` are reads/helpers.
- `cancel`, `extend`, `exempt`, and `delete` are reviewed-plan writes.
- `cancel` requires `--ack-irreversible` because official docs say canceled submissions cannot be reactivated and the contact must resubmit the form.
- `delete` requires `--ack-irreversible`; official docs mark Delete Intake Form Submission as Developer Preview.
- The official Count Submissions By Intake Form Ids endpoint uses `/_api/intake-forms/v1/submissions/count`, and the other submission methods use the same `/_api/intake-forms/v1/submissions...` root.
- Official Wix docs say these methods use `Read Intake Form` / `SCOPE.INTAKE-FORM.READ` for reads and `Manage Intake Form (PII)` / `SCOPE.INTAKE-FORM.MANAGE_LIMITED` for writes.

## Community Groups

- `wix-safe-agent-cli community-groups list [--params-json '{...}']`
- `wix-safe-agent-cli community-groups get --group-id <group_id>`
- `wix-safe-agent-cli community-groups get-by-slug --slug <slug>`
- `wix-safe-agent-cli community-groups query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-groups create --group-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-groups update --group-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-groups delete --group-id <group_id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json community-groups create --group-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json community-groups update --group-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-groups delete --group-id <group_id> [--receipt-out receipt.json]`

Notes for Community Groups:
- `community-groups list`, `get`, `get-by-slug`, and `query` are read commands for Wix Community Groups.
- `community-groups create` and `update` are reviewed-plan writes.
- `community-groups delete` requires `--ack-irreversible` because it removes a community group.
- Official Wix docs say list and query retrieve up to 100 groups, list defaults to created date descending, and query supports title filtering plus sorting by title, created date, member count, or recent activity date.
- Official Wix docs say secret groups are returned only to group admins and members.
- Official Wix docs say only group admins can update groups, changing a private group to public approves pending join requests, changing a private group to secret rejects pending join requests, and changing the group name may change the slug.
- Official Wix docs say group creation may become a pending create request depending on the site's dashboard setting.

## Community Group Rules

- `wix-safe-agent-cli community-group-rules list --group-id <group_id>`
- `wix-safe-agent-cli --plan-out plan.json community-group-rules create-or-replace --group-id <group_id> --rules-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-rules create-or-replace --group-id <group_id> --rules-json '{...}' [--receipt-out receipt.json]`

Notes for Community Group Rules:
- `community-group-rules list` reads rules for one group.
- `community-group-rules create-or-replace` is a reviewed-plan replacement write and requires `--ack-irreversible`.
- Official Wix docs say Create Or Replace All Rules creates rules if none exist, otherwise replaces all existing rules.
- Official Wix docs say only group admins can create or replace rules, both methods require visitor or member authentication, and rules are capped at 100 items.
- Group Rules Updated is callback-only and is not exposed as a CLI command.

## Community Group Requests

- `wix-safe-agent-cli community-group-requests list [--params-json '{...}']`
- `wix-safe-agent-cli community-group-requests query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-group-requests approve --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-group-requests reject --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-requests approve --request-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-requests reject --request-json '{...}' [--receipt-out receipt.json]`

Notes for Community Group Requests:
- `community-group-requests list` and `query` read group creation requests across a site.
- `community-group-requests approve` and `reject` are reviewed-plan writes and require `--ack-irreversible`.
- Official Wix docs say only Wix users can approve or reject group requests.
- Official Wix docs say `query` supports filtering by `status` and sorting by `createdDate`.
- Group Request Approved and Group Request Rejected are callback-only and are not exposed as CLI commands.

## Community Group Members

- `wix-safe-agent-cli community-group-members list --group-id <group_id> [--params-json '{...}']`
- `wix-safe-agent-cli community-group-members list-memberships --member-id <member_id> [--params-json '{...}']`
- `wix-safe-agent-cli community-group-members query --group-id <group_id> [--query-json '{...}']`
- `wix-safe-agent-cli community-group-members query-memberships --member-id <member_id> [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-group-members add --group-id <group_id> --members-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-group-members remove --group-id <group_id> --members-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-members add --group-id <group_id> --members-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-members remove --group-id <group_id> --members-json '{...}' [--receipt-out receipt.json]`

Notes for Community Group Members:
- `community-group-members list` and `query` read members of one group.
- `community-group-members list-memberships` and `query-memberships` read one site member's group memberships.
- `community-group-members add` and `remove` are reviewed-plan writes and require `--ack-irreversible`.
- Official Wix docs say adding members to a public group adds them right away, while private members receive an invitation to join.
- Official Wix docs say only group admins can remove members from their group.
- Member Added and Member Removed are callback-only and are not exposed as CLI commands.

## Community Group Roles

- `wix-safe-agent-cli --plan-out plan.json community-group-roles assign --group-id <group_id> --role-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-group-roles unassign --group-id <group_id> --role-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-roles assign --group-id <group_id> --role-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-group-roles unassign --group-id <group_id> --role-json '{...}' [--receipt-out receipt.json]`

Notes for Community Group Roles:
- `community-group-roles assign` assigns a role to existing group members and is a reviewed-plan write.
- `community-group-roles unassign` unassigns a role from group members and is a reviewed-plan write.
- Official Wix docs say assigning a role overrides the group member's current `role.value`.
- Official Wix docs say only `ADMIN` roles can be unassigned and that using unassign on members with `role.value` set to `MEMBER` returns an error.
- Official Wix docs say only group admins can call these methods, and assign cannot create members while unassign cannot remove members.
- Role Assigned To Group Member and Role Unassigned From Group Member are callback-only and are not exposed as CLI commands.

## Community Join Requests

- `wix-safe-agent-cli community-join-requests list --group-id <group_id> [--params-json '{...}']`
- `wix-safe-agent-cli community-join-requests query --group-id <group_id> [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-join-requests approve --group-id <group_id> --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-join-requests reject --group-id <group_id> --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-join-requests approve --group-id <group_id> --request-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-join-requests reject --group-id <group_id> --request-json '{...}' [--receipt-out receipt.json]`

Notes for Community Join Requests:
- `community-join-requests list` and `query` read pending or historical join requests for one group.
- `community-join-requests approve` and `reject` are reviewed-plan writes and require `--ack-irreversible`.
- Official Wix docs say this family is only relevant for private groups.
- Official Wix docs say approving a request adds the site member to the group.
- Official Wix docs say group managers always have access, and some group settings allow group members to approve or reject requests.
- Join Group Request Approved and Join Group Request Rejected are callback-only and are not exposed as CLI commands.

## Community Membership Questions

- `wix-safe-agent-cli community-membership-questions list --group-id <group_id>`
- `wix-safe-agent-cli community-membership-questions list-answers --group-id <group_id> [--member-ids-json '["member_id"]'] [--paging-json '{"limit":20}']`
- `wix-safe-agent-cli --plan-out plan.json community-membership-questions create-or-replace --group-id <group_id> --questions-json '{"questions":[...]}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-membership-questions create-or-replace --group-id <group_id> --questions-json '{"questions":[...]}' [--receipt-out receipt.json]`

Notes for Community Membership Questions:
- `community-membership-questions list` reads the membership questions for one group.
- `community-membership-questions list-answers` reads answers to those questions using explicit official `memberIds` and `paging` inputs.
- `community-membership-questions create-or-replace` is a reviewed-plan write and requires `--ack-irreversible`.
- Official Wix docs say create-or-replace creates membership questions if none exist, otherwise replaces all existing questions.
- `--questions-json` must be Wix's official object with a `questions` array. Providing an empty questions array means members will not have to answer any question when joining the group.
- Official Wix docs say only group admins can create or replace membership questions.

## Community Comments

- `wix-safe-agent-cli --plan-out plan.json community-comments create --comment-json '{...}'`
- `wix-safe-agent-cli community-comments get --comment-id <comment_id>`
- `wix-safe-agent-cli --plan-out plan.json community-comments update --comment-id <comment_id> --comment-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-comments delete --comment-id <comment_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-comments delete --comment-id <comment_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json community-comments moderate-draft-content --comment-id <comment_id> [--request-json '{...}']`
- `wix-safe-agent-cli community-comments query [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-comments mark --comment-id <comment_id> [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-comments unmark --comment-id <comment_id> [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-comments hide --comment-id <comment_id> [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-comments publish --comment-id <comment_id> [--request-json '{...}']`
- `wix-safe-agent-cli community-comments count [--request-json '{...}']`
- `wix-safe-agent-cli community-comments list-by-resource [--params-json '{...}']`
- `wix-safe-agent-cli community-comments get-thread --comment-id <comment_id> [--params-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-comments bulk-publish --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-comments bulk-hide --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-comments bulk-delete --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-comments bulk-moderate-draft-content --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-comments bulk-move-by-filter --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-comments bulk-delete --request-json '{...}' [--receipt-out receipt.json]`

Notes for Community Comments:
- `community-comments get`, `query`, `count`, `list-by-resource`, and `get-thread` read comment records, counts, or threads.
- `community-comments create` and `update` are reviewed-plan writes.
- `community-comments delete`, `moderate-draft-content`, `mark`, `unmark`, `hide`, `publish`, and all bulk commands require `--ack-irreversible`.
- Official Wix docs say Delete Comment deletes the comment content and sets status to `DELETED`.
- Official Wix docs say bulk publish, hide, delete, moderate, and move commands work by official filter and can affect multiple comments.
- Comment Deleted, Comment Content Changed, Comment Hidden, Comment Marked, Comment Moved, Comment Published, Comment Unmarked, Comment Created, Resource Comment Count Changed, and Comment Updated are callback-only and are not exposed as CLI commands.

## Community Reports V2

- `wix-safe-agent-cli community-reports get --report-id <report_id>`
- `wix-safe-agent-cli community-reports query [--query-json '{...}']`
- `wix-safe-agent-cli community-reports count-by-reason-types [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-reports create --report-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reports update --report-id <report_id> --report-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reports upsert --entity-name <entity_name> --entity-id <entity_id> --report-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reports delete --report-id <report_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-reports delete --report-id <report_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json community-reports bulk-delete-by-filter --filter-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-reports bulk-delete-by-filter --filter-json '{...}' [--receipt-out receipt.json]`

Notes for Community Reports V2:
- `community-reports get`, `query`, and `count-by-reason-types` read report records or report counts.
- `community-reports create`, `update`, and `upsert` are reviewed-plan writes.
- `community-reports delete` and `bulk-delete-by-filter` require `--ack-irreversible`.
- Official Wix docs say deleting a report removes it from the dashboard report list, and bulk-delete-by-filter deletes multiple reports by filter.
- Report Created, Report Deleted, Entity Report Summary Changed, and Report Updated are callback-only and are not exposed as CLI commands.

## Community Reviews

- `wix-safe-agent-cli community-reviews get --review-id <review_id> [--params-json '{"returnPrivateReviews":true}']`
- `wix-safe-agent-cli community-reviews query [--request-json '{...}']`
- `wix-safe-agent-cli community-reviews count [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-reviews create --review-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reviews update --review-id <review_id> --review-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reviews delete --review-id <review_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-reviews delete --review-id <review_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json community-reviews bulk-create --request-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reviews bulk-delete --filter-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-reviews remove-reply --review-id <review_id>`
- `wix-safe-agent-cli --plan-out plan.json community-reviews set-reply --review-id <review_id> --message <message>`
- `wix-safe-agent-cli --plan-out plan.json community-reviews update-moderation-status --review-id <review_id> --status <status>`
- `wix-safe-agent-cli --plan-out plan.json community-reviews bulk-update-moderation-status --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-reviews bulk-update-moderation-status --request-json '{...}' [--receipt-out receipt.json]`

Notes for Community Reviews:
- Official Wix docs say Reviews is currently only available with the `stores` namespace.
- `community-reviews get`, `query`, and `count` read review records or counts.
- `community-reviews create`, `update`, and `set-reply` are reviewed-plan writes.
- `community-reviews delete`, `bulk-create`, `bulk-delete`, `remove-reply`, `update-moderation-status`, and `bulk-update-moderation-status` require `--ack-irreversible`.
- Official Wix docs say update requires the current `review.revision`.
- Review Created, Review Deleted, Review Moderation Status Changed, Review Published, and Review Updated are callback-only and are not exposed as CLI commands.

## Community Review Requests

- `wix-safe-agent-cli --plan-out plan.json community-review-requests create --review-request-json '{...}'`
- `wix-safe-agent-cli community-review-requests get --review-request-id <review_request_id>`
- `wix-safe-agent-cli --plan-out plan.json community-review-requests delete --review-request-id <review_request_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-review-requests delete --review-request-id <review_request_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli community-review-requests query [--request-json '{...}']`
- `wix-safe-agent-cli community-review-requests count [--request-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json community-review-requests bulk-cancel-by-filter --filter-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-review-requests bulk-cancel-by-filter --filter-json '{...}' [--receipt-out receipt.json]`

Notes for Community Review Requests:
- Official Wix docs say Review Requests is currently only available with the `stores` namespace.
- `community-review-requests get`, `query`, and `count` read review request records or counts.
- `community-review-requests create` is a reviewed-plan write.
- `community-review-requests delete` and `bulk-cancel-by-filter` require `--ack-irreversible`.
- Official Wix docs say only review requests with `status` set to `CANCELED` can be deleted.
- Official Wix docs say bulk-cancel-by-filter starts a bulk job and returns a job ID. This CLI exposes the explicit cancel method but does not add a generic async-job runner.
- Review Request Created, Review Request Deleted, and Review Request Updated are callback-only and are not exposed as CLI commands.

## Community Moderation Rules

- `wix-safe-agent-cli --plan-out plan.json community-moderation-rules create --rule-json '{...}'`
- `wix-safe-agent-cli community-moderation-rules get --rule-id <rule_id>`
- `wix-safe-agent-cli --plan-out plan.json community-moderation-rules update --rule-id <rule_id> --rule-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json community-moderation-rules delete --rule-id <rule_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json community-moderation-rules delete --rule-id <rule_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli community-moderation-rules query [--request-json '{...}']`
- `wix-safe-agent-cli community-moderation-rules check-content --request-json '{...}'`

Notes for Community Moderation Rules:
- `community-moderation-rules get`, `query`, and `check-content` read rules or return moderation actions for submitted content.
- `community-moderation-rules create`, `update`, and `delete` are reviewed-plan writes and require `--ack-irreversible`.
- Official Wix docs say you can create up to 20 rules per namespace, every trigger needs a separate rule, and content is checked only for newly submitted reviews and comments.
- Official Wix docs say update requires the current `rule.revision`.
- Rule Created, Rule Deleted, and Rule Updated are callback-only and are not exposed as CLI commands.

## Inbox Conversations

- `wix-safe-agent-cli inbox-conversations get --conversation-id <conversation_id>`
- `wix-safe-agent-cli --plan-out plan.json inbox-conversations get-or-create --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json inbox-conversations get-or-create --request-json '{...}' [--receipt-out receipt.json]`

Notes for Inbox Conversations:
- `inbox-conversations get` reads one conversation.
- `inbox-conversations get-or-create` is a reviewed-plan write because it can create a conversation for the participant.
- Conversations Merged is callback-only and is not exposed as a CLI command.

## Inbox Messages

- `wix-safe-agent-cli inbox-messages list [--params-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json inbox-messages send --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json inbox-messages send --request-json '{...}' [--receipt-out receipt.json]`

Notes for Inbox Messages:
- `inbox-messages list` reads messages in a conversation. Official docs return up to 30 messages per request.
- `inbox-messages send` is a reviewed-plan write and requires `--ack-irreversible` because it sends a message to the business or participant and can send notifications.
- Button Interacted, Message Sent To Business, and Message Sent To Participant are callback-only and are not exposed as CLI commands.
- The current official Inbox menu has Conversations and Messages method pages, but no separate callable Channels method page.

## Loyalty Program

- `wix-safe-agent-cli loyalty-program get`
- `wix-safe-agent-cli loyalty-program premium-features`
- `wix-safe-agent-cli --plan-out plan.json loyalty-program update --program-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-program update --program-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-program activate`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-program activate [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-program pause`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-program pause [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-program enable-points-expiration`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-program enable-points-expiration [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-program disable-points-expiration`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-program disable-points-expiration [--receipt-out receipt.json]`

Notes for Loyalty Program:
- `loyalty-program get` reads the current loyalty program.
- `loyalty-program premium-features` reads premium feature availability for loyalty program, tiers, and points expiration.
- `loyalty-program update` requires an official body with a `loyaltyProgram` object and updates the program name or point definition.
- `loyalty-program activate`, `pause`, `enable-points-expiration`, and `disable-points-expiration` are status/settings writes.
- All Loyalty Program writes are reviewed-plan writes and require `--ack-irreversible` because they change program-wide loyalty settings, status, or points-expiration behavior.
- Loyalty Program Updated is callback-only and is not exposed as a CLI command.

## Loyalty Earning Rules

- `wix-safe-agent-cli loyalty-earning-rules list [--params-json '{"triggerAppId":"..."}']`
- `wix-safe-agent-cli loyalty-earning-rules get --rule-id <rule_id>`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules create --rule-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules create --rule-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules update --rule-id <rule_id> --rule-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules update --rule-id <rule_id> --rule-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules delete --rule-id <rule_id> --revision <revision>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules delete --rule-id <rule_id> --revision <revision> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules bulk-create --rules-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules bulk-create --rules-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules create-custom --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules create-custom --request-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-earning-rules delete-automation --rule-id <rule_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-earning-rules delete-automation --rule-id <rule_id> [--receipt-out receipt.json]`

Notes for Loyalty Earning Rules:
- `loyalty-earning-rules list` reads automated and non-automated earning rules. Official docs allow filtering by `triggerAppId` or `triggerActivityType`.
- `loyalty-earning-rules get` reads one non-automated earning rule.
- `loyalty-earning-rules create` and `bulk-create` create non-automated earning rules from Wix's supported list.
- `loyalty-earning-rules update` supports partial updates and requires the current `earningRule.revision`.
- `loyalty-earning-rules delete` deletes one non-automated earning rule and requires the current `revision` query value.
- `loyalty-earning-rules create-custom` creates a custom automated earning rule.
- `loyalty-earning-rules delete-automation` deletes a custom automated earning rule. Official docs say pre-installed automated rules can only be paused.
- All Earning Rules writes are reviewed-plan writes and require `--ack-irreversible` because they change how customers earn loyalty points.
- The official method endpoint headers and fetch examples use the `/_api/loyalty-earning-rules` root, while some curl examples omit `/_api`; this CLI follows the endpoint headers and fetch examples.
- Earning Rule Created, Earning Rule Updated, and Earning Rule Deleted are callback-only and are not exposed as CLI commands.

## Loyalty Tiers

- `wix-safe-agent-cli loyalty-tiers list`
- `wix-safe-agent-cli loyalty-tiers get --tier-id <tier_id>`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers create --tier-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers create --tier-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers update --tier-id <tier_id> --tier-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers update --tier-id <tier_id> --tier-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers delete --tier-id <tier_id> --revision <revision>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers delete --tier-id <tier_id> --revision <revision> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers bulk-create --tiers-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers bulk-create --tiers-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers get-program`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers get-program [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers create-program-settings --program-settings-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers create-program-settings --program-settings-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli loyalty-tiers get-program-settings`
- `wix-safe-agent-cli --plan-out plan.json loyalty-tiers update-program-settings --program-settings-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-tiers update-program-settings --program-settings-json '{...}' [--receipt-out receipt.json]`

Notes for Loyalty Tiers:
- `loyalty-tiers list`, `get`, and `get-program-settings` are reads.
- `loyalty-tiers create` creates one loyalty tier. Official docs say a site must have a Plus or Business plan to add tiers.
- `loyalty-tiers update` changes tier-specific settings such as name and required points.
- `loyalty-tiers delete` deletes one tier and requires the current `revision` query value.
- `loyalty-tiers bulk-create` creates up to 20 tiers.
- `loyalty-tiers get-program` returns tiers and program settings. It is guarded because official docs say it creates default program settings if none exist.
- `loyalty-tiers create-program-settings` creates global settings for all tiers.
- `loyalty-tiers update-program-settings` changes global settings for all tiers. Official docs say `programSettings.status`, `programSettings.revision`, and `programSettings.rollingWindow` are required.
- All Loyalty Tiers writes are reviewed-plan writes and require `--ack-irreversible` because they change tier definitions, thresholds, or global tier program settings.
- Tier Created, Tier Updated, and Tier Deleted are callback-only and are not exposed as CLI commands.

## Loyalty Accounts

- `wix-safe-agent-cli loyalty-accounts query [--query-json '{...}']`
- `wix-safe-agent-cli loyalty-accounts search [--search-json '{...}']`
- `wix-safe-agent-cli loyalty-accounts count [--count-json '{...}']`
- `wix-safe-agent-cli loyalty-accounts get --account-id <account_id>`
- `wix-safe-agent-cli loyalty-accounts get-program-totals`
- `wix-safe-agent-cli loyalty-accounts get-current-member-account`
- `wix-safe-agent-cli loyalty-accounts get-by-secondary-id (--contact-id <contact_id> | --member-id <member_id>)`
- `wix-safe-agent-cli loyalty-accounts list [--params-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json loyalty-accounts create --account-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-accounts create --account-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-accounts adjust-points --account-id <account_id> --adjust-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-accounts adjust-points --account-id <account_id> --adjust-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-accounts bulk-adjust-points --adjust-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-accounts bulk-adjust-points --adjust-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-accounts earn-points --account-id <account_id> --earn-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-accounts earn-points --account-id <account_id> --earn-json '{...}' [--receipt-out receipt.json]`

Notes for Loyalty Accounts:
- `loyalty-accounts list` is deprecated by Wix and exposed only for compatibility. Prefer `query` or `search`.
- `loyalty-accounts get`, `query`, `search`, `count`, `get-program-totals`, `get-current-member-account`, and `get-by-secondary-id` read loyalty accounts or account totals. Official docs say query defaults to `createdDate ASC`, `paging.limit` 100, and `paging.offset` 0.
- `loyalty-accounts get-by-secondary-id` requires exactly one of `--contact-id` or `--member-id`.
- `loyalty-accounts create` creates one loyalty account for a site contact. Official docs say the site needs an active loyalty program and the request needs a contact ID.
- `loyalty-accounts adjust-points` changes one account's point balance. The CLI requires the current `revision` and exactly one of `balance` or `amount`.
- `loyalty-accounts bulk-adjust-points` changes multiple account balances and returns an `asyncJobId`; this CLI requires a `search` selector to avoid accidental all-account changes, and you can use the named `async-jobs` commands if you need to inspect that job.
- `loyalty-accounts earn-points` adds positive points to one account. Official docs require `amount`, `appId`, and `idempotencyKey`.
- All Loyalty Accounts writes are reviewed-plan writes and require `--ack-irreversible` because they create customer loyalty accounts or change point balances.
- Loyalty Account Created, Points Updated, Account Reward Availability Updated, and Loyalty Account Updated are callback-only and are not exposed as CLI commands.

## Loyalty Transactions

- `wix-safe-agent-cli loyalty-transactions get --transaction-id <transaction_id>`
- `wix-safe-agent-cli loyalty-transactions query [--query-json '{...}']`

Notes for Loyalty Transactions:
- `loyalty-transactions get` retrieves one loyalty transaction.
- `loyalty-transactions query` retrieves loyalty transactions with official query filtering, sorting, and paging.
- Official docs say transactions cover account activity such as `EARN`, `REDEEM`, `ADJUST`, `REFUND`, `EXPIRE`, and `EARN_ATTEMPT`.
- These commands are read-only and do not expose any write action.

## Loyalty Social Media

- `wix-safe-agent-cli loyalty-social-media list`
- `wix-safe-agent-cli --plan-out plan.json loyalty-social-media create --followed-channel-json '{"followedChannel":{"channel":"X"}}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-social-media create --followed-channel-json '{"followedChannel":{"channel":"X"}}' [--receipt-out receipt.json]`

Notes for Loyalty Social Media:
- `loyalty-social-media list` reads the followed social media channels for the current visitor/member identity.
- `loyalty-social-media create` records a followed social media channel and is a reviewed-plan write with `--ack-irreversible` because it can award loyalty points.
- Official docs say both methods require visitor or member authentication, and members can only follow channels enabled in the dashboard.
- Followed Channel Created is callback-only and is not exposed as a CLI command.

## Loyalty Imports

- `wix-safe-agent-cli loyalty-imports get --import-id <import_id>`
- `wix-safe-agent-cli loyalty-imports query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json loyalty-imports create-file-url`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json loyalty-imports create-file-url [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-imports create --import-json '{"fileUrl":"wixmp://...","fileName":"points.csv","fileSize":1200}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-imports create --import-json '{"fileUrl":"wixmp://...","fileName":"points.csv","fileSize":1200}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-imports execute --execute-json '{"loyaltyImportId":"<import_id>","headerMappingInfo":{"headerMappings":[{"columnName":"email","columnIndex":0},{"columnName":"points","columnIndex":1}]}}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-imports execute --execute-json '{"loyaltyImportId":"<import_id>","headerMappingInfo":{"headerMappings":[{"columnName":"email","columnIndex":0},{"columnName":"points","columnIndex":1}]}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli loyalty-imports get-error-file-download-url --import-id <import_id>`

Notes for Loyalty Imports:
- `loyalty-imports get`, `query`, and `get-error-file-download-url` read import status or helper URLs.
- `loyalty-imports create-file-url` creates the official upload URL and file path for the import flow. It is a reviewed-plan helper write, but it does not require `--ack-irreversible`.
- `loyalty-imports create` creates a loyalty import from an uploaded CSV file URL. `loyalty-imports execute` starts the import after the object reaches `PARSED`. Both require `--ack-irreversible` because imports can overwrite customer point balances.
- Official docs say the import file must be CSV, needs customer email and points balance columns, can continue despite row-level errors, and has a 10MB max file size.
- Loyalty Import Created is callback-only and is not exposed as a CLI command.

## Loyalty Rewards

- `wix-safe-agent-cli loyalty-rewards list [--params-json '{...}']`
- `wix-safe-agent-cli loyalty-rewards get --reward-id <reward_id>`
- `wix-safe-agent-cli loyalty-rewards query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json loyalty-rewards create --reward-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-rewards create --reward-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-rewards bulk-create --rewards-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-rewards bulk-create --rewards-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-rewards update --reward-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-rewards update --reward-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-rewards delete --reward-id <reward_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-rewards delete --reward-id <reward_id> [--receipt-out receipt.json]`

Notes for Loyalty Rewards:
- `loyalty-rewards list`, `get`, and `query` read customer-redeemable reward definitions. Official docs say list includes rewards that are not currently redeemable because customers do not have enough points.
- `loyalty-rewards query` adds the official default `cursorPaging.limit` 50 when the request does not include a limit.
- `loyalty-rewards create`, `bulk-create`, `update`, and `delete` are reviewed-plan writes and require `--ack-irreversible` because they change what customers can redeem with loyalty points.
- Official docs say `active` defaults to `false`, a reward's `type` cannot be changed after creation, and tier-specific reward costs or discounts use `configsByTier`.
- Reward Created, Reward Deleted, and Reward Updated are callback-only and are not exposed as CLI commands.

## Loyalty Checkout Discounts

- `wix-safe-agent-cli loyalty-checkout-discounts query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json loyalty-checkout-discounts apply --discount-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-checkout-discounts apply --discount-json '{...}' [--receipt-out receipt.json]`

Notes for Loyalty Checkout Discounts:
- `loyalty-checkout-discounts query` retrieves loyalty checkout discounts. The CLI adds the official default `paging.limit` 50 and `createdDate` descending sort when omitted.
- `loyalty-checkout-discounts apply` applies one reward, loyalty coupon, or referral reward to a checkout and is a reviewed-plan write with `--ack-irreversible`.
- Official docs say a site must have Wix Loyalty Program installed and must also have Wix Bookings, Wix Stores, or Wix Restaurants Orders (New).
- The apply body must include `checkoutId` and exactly one of `rewardId`, `loyaltyCouponId`, or `referralRewardId`.

## Loyalty Coupons

- `wix-safe-agent-cli loyalty-coupons get --coupon-id <coupon_id>`
- `wix-safe-agent-cli loyalty-coupons query [--query-json '{...}']`
- `wix-safe-agent-cli loyalty-coupons get-current-member`
- `wix-safe-agent-cli --plan-out plan.json loyalty-coupons redeem-current-member --redeem-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-coupons redeem-current-member --redeem-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-coupons redeem --redeem-json '{...}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-coupons redeem --redeem-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json loyalty-coupons delete --coupon-id <coupon_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json loyalty-coupons delete --coupon-id <coupon_id> [--receipt-out receipt.json]`

Notes for Loyalty Coupons:
- `loyalty-coupons get`, `query`, and `get-current-member` read loyalty coupon records.
- `loyalty-coupons redeem-current-member`, `redeem`, and `delete` are reviewed-plan writes and require `--ack-irreversible` because they redeem loyalty points or remove loyalty coupon records.
- Official docs say a loyalty coupon creates a corresponding reference coupon, and deleting the loyalty coupon does not affect that reference coupon.
- Coupon Created and Coupon Deleted are callback-only and are not exposed as CLI commands.

## Email Subscriptions

- `wix-safe-agent-cli email-subscriptions query [--query-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json email-subscriptions upsert --subscription-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json email-subscriptions bulk-upsert --subscriptions-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json email-subscriptions generate-unsubscribe-link --email <email>`
- `wix-safe-agent-cli --plan-out plan.json email-subscriptions generate-unsubscribe-link --request-json '{...}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-subscriptions upsert --subscription-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-subscriptions bulk-upsert --subscriptions-json '{...}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json email-subscriptions generate-unsubscribe-link --email <email> [--receipt-out receipt.json]`

Notes for Email Subscriptions:
- All Email Subscriptions methods are marked Developer Preview in official Wix docs.
- `email-subscriptions query` is a read/helper command. Official docs currently support querying by `email` with the `$in` array filter.
- `email-subscriptions upsert` and `bulk-upsert` are reviewed-plan writes because they create or update contacts' email subscription status.
- `email-subscriptions generate-unsubscribe-link` is a reviewed-plan helper write. Official docs say the recipient's status changes to `UNSUBSCRIBED` only if someone clicks the link and confirms unsubscribe.
- Official Wix docs say these methods require Wix app or Wix user identity auth and permission `Manage Email Subscriptions`.
- Email Subscription Changed is callback-only and is not exposed as a CLI command.

## Form submissions (read/helper and write)

- `wix-safe-agent-cli form-submissions get-submission --submission-id <submission-id>`
- `wix-safe-agent-cli form-submissions query-submissions-by-namespace --query-json '{...}' [--only-your-own true|false]`
- `wix-safe-agent-cli form-submissions count-submissions --form-ids-json '["<form_id>"]' --namespace <namespace> [--statuses-json '[...]']`
- `wix-safe-agent-cli form-submissions get-media-upload-url --form-id <form_id> --filename <filename> --mime-type <mime-type>`
- `wix-safe-agent-cli form-submissions create-submission --submission-json '{...}'`
- `wix-safe-agent-cli form-submissions update-submission --submission-json '{...}'`
- `wix-safe-agent-cli form-submissions delete-submission --submission-id <submission-id> [--permanent true|false] [--preserve-files true|false]`
- `wix-safe-agent-cli form-submissions confirm-submission --submission-id <submission-id>`
- `wix-safe-agent-cli form-submissions bulk-mark-submissions-as-seen --form-id <form_id> --ids-json '[...]' [--all-unseen]`

Notes for Form Submissions:
- Every `form-submissions` command first checks app instance state and refuses unless the target site has `wix_forms` installed.
- `get-submission`, `query-submissions-by-namespace`, `count-submissions`, and `get-media-upload-url` are read/helper methods.
- `query-submissions-by-namespace` is read-only, requires `--query-json`, and requires namespace inside query filter scope.
- `query-submissions-by-namespace` supports optional top-level `onlyYourOwn` via `--only-your-own`.
- `count-submissions` is read-only, requires top-level `formIds` and `namespace`.
- `count-submissions` supports optional top-level `statuses`.
- `get-media-upload-url` is non-mutating helper, returning an upload URL.
- `get-media-upload-url` sends `formId`, `filename`, and `mimeType` in the request body.
- All form-submissions write commands are reviewed-plan write commands: plan first with a dry-run preview, then live apply with `--plan-in --apply --yes`.
- `delete-submission` is destructive and also requires `--ack-irreversible` at apply time.
- `bulk-mark-submissions-as-seen` refuses the empty-ID case unless `--all-unseen` is explicitly set.
- `update-submission` checks the submission `revision` before planning and apply.
- `confirm-submission` works only when the current submission status is `PENDING`.
- Every form-submissions call first performs an app-instance check and requires `wix_forms` installed on the target site.

## Read AI credits (account-level)

- `wix-safe-agent-cli ai-credits get-balance`

Notes for AI Credits:
- This command uses `WIX_API_KEY` only in this boundary and sends `Authorization` only.
- The official `get-balance` method page marks this API as Developer Preview.
- The official intro says the balance scope can vary by caller access, but this tool ships the API-key path only and treats the result as account-level coverage.
- The command is read-only and has no write flow.

## Read analytics data

- `wix-safe-agent-cli analytics-data get --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> --measurement-types-json '["TOTAL_SALES","TOTAL_ORDERS"]' [--time-zone <tz>]`

Notes for Analytics Data:
- This command uses Wix app or Wix user identity auth, which resolves through the repo’s site-context auth path.
- The live request sends Wix's published parameter names: `dateRange.startDate`, `dateRange.endDate`, `measurementTypes`, and optional `timeZone`.
- `measurementTypes` accepts these values only: `TOTAL_SALES`, `TOTAL_ORDERS`, `CLICKS_TO_CONTACT`, `TOTAL_SESSIONS`, `TOTAL_FORMS_SUBMITTED`, `TOTAL_UNIQUE_VISITORS`.
- `timeZone` is optional.
- `start-date` and `end-date` must be `YYYY-MM-DD` local dates and `start-date` must be before or equal to `end-date`.
- Wix's official method docs also note that site analytics data is limited to the recent 62-day window, so older `start-date` values are refused before request send.
- This command calls `GET /analytics/v2/site-analytics/data`.
- This boundary is read-only and uses the app-token / stored-token auth path only.
- This boundary is locally unit-tested and live-unverified.

## Read analytics semantic models

- `wix-safe-agent-cli analytics-semantic-models list`
- `wix-safe-agent-cli analytics-semantic-models get --semantic-model-id <semantic_model_id>`
- `wix-safe-agent-cli analytics-semantic-models query --query-json '{"semanticModelId":"<semantic_model_id>","interval":{"from":"<yyyy-mm-dd>","to":"<yyyy-mm-dd>"}}'`

Notes for Analytics Semantic Models:
- These commands use Wix app or Wix user identity auth for the current site context.
- This family needs `Site Analytics - read permissions`.
- `analytics-semantic-models list` calls `GET /analytics/semantic-model/v3/semantic-models`.
- `analytics-semantic-models get` calls `GET /analytics/semantic-model/v3/semantic-models/{semanticModelId}` and requires a non-empty `--semantic-model-id`.
- `analytics-semantic-models query` calls `POST /analytics/semantic-model/v3/semantic-models/query-data`.
- `--query-json` must be the official top-level query object and must include an `interval` object because Wix docs say semantic-model queries cannot run without a date range.
- Wix docs also say field names must match `Get Semantic Model`, some fields have dependencies, one query can return up to 1,000 rows, and `paging.limit` defaults to `50` with `paging.offset` defaulting to `0`.
- This boundary is read-only, locally unit-tested, and live-unverified.

## Manage analytics sessions

- `wix-safe-agent-cli analytics-sessions get-list-job-result --job-id <job_id> --limit <1-1000> --offset <0+>`
- `wix-safe-agent-cli --plan-out plan.json analytics-sessions list-async --sessions-json '{"deviceType":{"type":"DESKTOP"},"predefinedTimePeriod":"LAST_7_DAYS"}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json analytics-sessions list-async --sessions-json '{"deviceType":{"type":"DESKTOP"},"predefinedTimePeriod":"LAST_7_DAYS"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json analytics-sessions mark-recordings-deleted --session-ids-json '{"sessionIds":["<session_id>"]}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json analytics-sessions mark-recordings-deleted --session-ids-json '{"sessionIds":["<session_id>"]}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json analytics-sessions mark-session-recorded --session-id <session_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json analytics-sessions mark-session-recorded --session-id <session_id> [--receipt-out receipt.json]`

Notes for Analytics Sessions:
- Wix says this API is a beta feature available only to select beta users.
- These commands use Wix app or Wix user identity auth and require `Manage Session Recording Analytics - all permissions`.
- `analytics-sessions get-list-job-result` calls `GET /analytics/v1/sessions/list/result` with required `jobId`, `limit`, and `offset` query parameters.
- `analytics-sessions list-async` calls `POST /analytics/v1/sessions/list/async` as a reviewed-plan async job starter. It requires one official session filter (`navigationFlow`, `conversionFunnel`, or `deviceType`) and one official time period (`customTimePeriod` or `predefinedTimePeriod`).
- `analytics-sessions mark-recordings-deleted` calls `POST /analytics/v1/sessions/recordings-deleted` and accepts 1 to 100 browser session IDs.
- `analytics-sessions mark-session-recorded` calls `POST /analytics/v1/sessions/session-recorded`.
- The two recording-state mutation commands require `--ack-irreversible`.
- This boundary is locally unit-tested and live-unverified. It does not expose a generic async job runner.

## Manage Automations storage items

- `wix-safe-agent-cli --plan-out plan.json automation-storage-items create --storage-item-json '{"storageItem":{"key":"<key>","displayName":"<name>","type":"STRING","stringValue":{"value":"<value>"}}}'`
- `wix-safe-agent-cli automation-storage-items get --key <key> [--consistent-read true]`
- `wix-safe-agent-cli automation-storage-items query --query-json '{...}'`
- `wix-safe-agent-cli --plan-out plan.json automation-storage-items bulk-update-tags --tags-json '{"storageItemIds":["<id>"],"assignTags":{"publicTags":{"tagIds":["<tag_id>"]}}}'`
- `wix-safe-agent-cli --plan-out plan.json automation-storage-items bulk-update-tags-by-filter --tags-json '{"filter":{},"assignTags":{"publicTags":{"tagIds":["<tag_id>"]}}}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json automation-storage-items bulk-update-tags-by-filter --tags-json '{"filter":{},"assignTags":{"publicTags":{"tagIds":["<tag_id>"]}}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json automation-storage-items update-counter-by --key <key> --value "1"`
- `wix-safe-agent-cli --plan-out plan.json automation-storage-items update-value --key <key> --value-json '{"stringValue":"<value>"}'`

Notes for Automations Storage Items:
- These commands use Wix app or Wix user identity auth for the current site context and require `Set Up Automations`.
- `create` calls `POST /storage-service/v1/storage-items` and requires `storageItem.key`, `storageItem.displayName`, and `storageItem.type`.
- `get` calls `GET /storage-service/v1/storage-items/{key}` and supports the official `consistentRead` query parameter.
- `query` calls `POST /storage-service/v1/storage-items/query`.
- `bulk-update-tags` calls `POST /storage-service/v1/bulk/storage-items/update-tags` and accepts 1 to 100 `storageItemIds`.
- `bulk-update-tags-by-filter` calls `POST /storage-service/v1/bulk/storage-items/update-tags-by-filter`, returns a `jobId`, and requires `--ack-irreversible` because an empty filter can update all storage items.
- `update-counter-by` calls `PATCH /storage-service/v1/storage-items/{key}/update-counter-by` with a positive or negative decimal string.
- `update-value` calls `PATCH /storage-service/v1/storage-items/{key}/update-value` and requires exactly one of `stringValue`, `booleanValue`, or `numberValue`.
- Wix docs say a site can have up to 100 storage items, storage item keys are immutable, type cannot change after create, and the site must have at least one automation before using storage items.
- Storage item events are callback-only. This family is locally unit-tested and live-unverified.

## Manage Automations V2

- `wix-safe-agent-cli --plan-out plan.json automations-v2 create --automation-json '{"automation":{...}}'`
- `wix-safe-agent-cli automations-v2 get --automation-id <automation_id>`
- `wix-safe-agent-cli --plan-out plan.json automations-v2 update --automation-json '{"automation":{"id":"<automation_id>","revision":"<revision>"}}'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json automations-v2 update --automation-json '{"automation":{"id":"<automation_id>","revision":"<revision>"}}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json automations-v2 delete --automation-id <automation_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json automations-v2 delete --automation-id <automation_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli automations-v2 query --query-json '{...}'`
- `wix-safe-agent-cli automations-v2 validate --automation-json '{"automation":{...}}'`

Notes for Automations V2:
- These commands use Wix app or Wix user identity auth for the current site context and require `Set Up Automations`.
- `create` calls `POST /automations-service/v2/automations` and is a reviewed-plan write requiring `--ack-irreversible` because the automation may be active.
- `get` calls `GET /automations-service/v2/automations/{automationId}`.
- `update` calls `PATCH /automations-service/v2/automations/{automation.id}` and requires `automation.id` plus the current `automation.revision`.
- `delete` calls `DELETE /automations-service/v2/automations/{automationId}` and requires `--ack-irreversible`.
- `query` calls `POST /automations-service/v2/automations/query`.
- `validate` calls `POST /automations-service/v2/automations/validate` and is a helper read for checking automation configuration before activation.
- Wix docs say trigger and action extensions must already exist, the apps that added them must already be installed, create/update do not validate configuration unless `validate` is called first, and currently only one root action is supported.
- Automation events are callback-only. This family is locally unit-tested and live-unverified.

## Read async job status and items

- `wix-safe-agent-cli async-jobs get --job-id <job_id>`
- `wix-safe-agent-cli async-jobs list-items --job-id <job_id>`

Notes for Async Jobs:
- These commands use Wix app or Wix user identity auth for the current site context.
- This family needs `READ ASYNC JOBS`.
- `async-jobs get` calls `GET /async-jobs/v1/async-jobs/{jobId}`.
- `async-jobs list-items` calls `GET /async-jobs/v1/async-jobs/{jobId}/items`.
- Both commands require a non-empty `--job-id`.
- This boundary is read-only, locally unit-tested, and live-unverified.

## Search site documents

- `wix-safe-agent-cli site-search search --document-type BLOG_POSTS|BOOKING_SERVICES|EVENTS|FORUM_CONTENT|ONLINE_PROGRAMS|PROGALLERY_ITEM|STORES_PRODUCTS --search-json '{...}' [--language <code>]`

Notes for Site Search:
- `site-search search` is the current shipped Wix Site Search boundary.
- This command uses Wix app or Wix user identity auth for the current site context.
- This family needs permission `Read Site Documents`.
- Official Wix docs also say the Wix Site Search app must be installed on the target site.
- `--document-type` is limited in this tool to the current official supported document types: `BLOG_POSTS`, `BOOKING_SERVICES`, `EVENTS`, `FORUM_CONTENT`, `ONLINE_PROGRAMS`, `PROGALLERY_ITEM`, and `STORES_PRODUCTS`.
- `--search-json` is the official `search` object and may include paging, filter, sort, free-text search, and aggregations.
- This command uses `POST /_api/site-search/v1/search`.
- Official Wix docs currently disagree on the exact REST URL: the main method page and curl example use `/_api/site-search/v1/search`, while the markdown schema shows a shortened `/v1/search` URL. This boundary follows the main method page path and keeps the mismatch documented.
- This boundary is read-only, locally unit-tested, and live-unverified.

## Read account records (account-level, contract-gated)

- `wix-safe-agent-cli accounts get --account-id <account_guid>`
- `wix-safe-agent-cli accounts list-child-accounts [--limit N] [--offset N]`

Notes for Accounts:
- These commands use account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`).
- Wix's official Accounts docs say this API is only open to companies with a signed contract with Wix.
- `accounts get` uses `GET /accounts/v1/accounts/{accountId}` and requires `--account-id`.
- `accounts get` is documented with permission `Account.GetAccountProperties` and scope `SCOPE.IDENTITY.MANAGE-TEAM-MEMBERS`.
- `accounts list-child-accounts` uses `GET /accounts/v1/account/child-accounts`.
- `accounts list-child-accounts` supports optional `--limit` and `--offset` via `paging.limit` and `paging.offset`.
- This boundary accepts `--limit` from `0` to `50` and requires `--offset` to be `0` or greater, matching the published method boundary.
- `accounts list-child-accounts` is documented with permission `ACCOUNT.CHILD_ACCOUNTS_LIST`.
- These commands are read-only and live-unverified.

## Read and change site contributors

- `wix-safe-agent-cli contributors query [--policy-ids-json '["6600344420111308827"]']`
- `wix-safe-agent-cli --plan-out plan.json contributors remove --account-id <account_id> --site-id <site_id>`
- `wix-safe-agent-cli --plan-out plan.json contributors change-role --account-id <account_id> --site-id <site_id> --role-ids-json '["<role_guid>"]'`
- `wix-safe-agent-cli --plan-out plan.json contributors change-contributor-location --account-id <account_id> --site-id <site_id> --location-ids-json '["<location_guid>"]'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json contributors remove --account-id <account_id> --site-id <site_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contributors change-role --account-id <account_id> --site-id <site_id> --role-ids-json '["<role_guid>"]' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json contributors change-contributor-location --account-id <account_id> --site-id <site_id> --location-ids-json '["<location_guid>"]' [--receipt-out receipt.json]`

Notes for Contributors:
- `contributors query` uses Wix app or Wix user identity for the current site context, not the account API-key path.
- `contributors remove`, `contributors change-role`, and `contributors change-contributor-location` use the same auth path, but this tool requires `--site-id` and sends `wix-site-id` on the preflight, live write, and verification requests so the target site stays explicit.
- The official method is `GET /roles-management/v2/contributors/query`.
- The official remove method is `POST /roles-management/contributor/remove` with JSON body `{"accountId":"..."}`.
- The official change-role method is `PUT /roles-management/contributor/change/role` with JSON body `{"accountId":"...","newRoles":[{"roleId":"..."}]}`.
- The official change-contributor-location method is `PUT /roles-management/contributor/change/locations` with JSON body `{"accountId":"...","newLocations":["..."]}`.
- The command supports the documented role filter only: optional `--policy-ids-json` maps to repeated `filter.policyIds` query parameters.
- If `--policy-ids-json` is omitted, the command requests the full contributor list for the current site context.
- `contributors remove` is plan-first, refuses apply unless `--apply --yes --ack-irreversible` is present, and verifies success by rerunning contributors query and confirming the removed `accountId` no longer appears.
- `contributors change-role` is plan-first, refuses apply unless `--apply --yes` is present, and verifies success by checking provider `newAssignedRoles` against the requested role GUIDs before rerunning contributors query and confirming the contributor still appears for the same site context.
- `contributors change-contributor-location` is plan-first, refuses apply unless `--apply --yes` is present, and verifies success by checking provider `newAssignedLocations` for the requested location GUIDs before rerunning contributors query and confirming the contributor still appears for the same site context.
- `contributors change-role` replaces all existing role assignments for that contributor, so callers must supply explicit role GUIDs in `--role-ids-json`.
- `contributors change-contributor-location` replaces all existing location assignments for that contributor's role assignments, so callers must supply explicit location GUIDs in `--location-ids-json`.
- The nearby `Get Roles Info` discovery API is beta-gated in Wix docs and is `excluded` from the shipped surface.
- Location lookup also remains `excluded` from the Contributors surface. Official Wix docs say to get location IDs from the Locations API.
- The official Contributors API is for customer access to one site, not company employee access across an account.
- The official permission scope for this method is `Manage Contributors` (`SCOPE.DC-IDENTITY.MANAGE-CONTRIBUTORS`).
- The official `change-contributor-location` method page currently lists permission `SITE_ROLES.CHANGE_LOCATION` and scope text `View SEO Settings: SCOPE.PROMOTE.VIEW-SEO`, and this tool keeps that mismatch explicit instead of normalizing it.
- Nearby `Users` and `Site Invites` methods are `excluded` in this boundary because the official docs say their account API-key path is currently limited to selected beta users.
- This boundary is locally unit-tested and live-unverified.

## Read sites (account-level)

- `wix-safe-agent-cli sites query [--query-json '{...}'] [--filter-json '{...}'] [--sort-json '{...}'] [--cursor <cursor>] [--limit N]`
- `wix-safe-agent-cli sites count [--query-json '{...}'] [--filter-json '{...}']`

Notes for Sites:
- Read Site Data permission required.
- This boundary sends account-level headers (`Authorization` + `wix-account-id`) for Sites commands.
- `sites query` supports up to `--limit 100` per request.
- `sites count` does not support `premium` or `appIds` filters.
- Free Wix accounts can return up to 1,000 sites in count results; premium accounts can return more.

## Read domains (account-level)

- `wix-safe-agent-cli domains check-availability --domain <domain>`
- `wix-safe-agent-cli domains suggest --query <query> [--tlds-json '["com","net"]'] [--paging-limit N] [--cursor <cursor>] [--max-length N]`

Notes for Domains:
- These commands use account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`) and target `GET /domain-search/v2/check-domain-availability` and `GET /domain-search/v2/suggest-domains`.
- `check-availability` requires `--domain` and rejects empty values.
- `check-availability` expects a domain that includes a TLD (for example, `example.com`).
- `suggest` requires `--query` and validates `--paging-limit` (1-20), `--max-length` (3-63), and `--tlds-json` (max 10 values, non-empty strings without a leading dot).
- Official Wix docs and SDK examples show mixed header descriptions for these calls. This boundary uses the repo’s account API key resolver (`Authorization` + `wix-account-id`) and does not expose any generic request bridge.
- This boundary is locally unit-tested and live-unverified.

## Manage Domain DNS zones (account-level)

- `wix-safe-agent-cli domain-dns get-zone --domain-name <domain.tld>`
- `wix-safe-agent-cli domain-dns preview-zone --domain-name <domain.tld>`
- `wix-safe-agent-cli --plan-out plan.json domain-dns create-zone --dns-zone-json '{"domainName":"example.com","records":[...]}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json domain-dns create-zone --dns-zone-json '{"domainName":"example.com","records":[...]}' --receipt-out receipt.json`
- `wix-safe-agent-cli --plan-out plan.json domain-dns update-zone --domain-name <domain.tld> [--additions-json '[...]'] [--deletions-json '[...]'] [--dnssec-enabled true|false]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json domain-dns update-zone --domain-name <domain.tld> [--additions-json '[...]'] [--deletions-json '[...]'] [--dnssec-enabled true|false] --receipt-out receipt.json`
- `wix-safe-agent-cli --plan-out plan.json domain-dns delete-zone --domain-name <domain.tld>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json domain-dns delete-zone --domain-name <domain.tld> --receipt-out receipt.json`

Notes for Domain DNS:
- These commands use account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`) and target:
  - `GET /domains/v1/dns-zones/{domainName}`
  - `GET /domains/v1/dns-zones/{domainName}/preview`
  - `POST /domains/v1/dns-zones`
  - `PATCH /domains/v1/dns-zones/{domainName}`
  - `DELETE /domains/v1/dns-zones/{domainName}`
- Both commands require `--domain-name`, enforce a hostname with TLD, and reject leading or trailing dots.
- `preview-zone` is read-only and returns a calculated DNS zone preview before a real connection flow.
- Wix docs say this API requires an account-level API key and not the standard auth header wording.
- `create-zone`, `update-zone`, and `delete-zone` are reviewed-plan writes in this tool.
- `delete-zone` always requires `--ack-irreversible`.
- `update-zone` requires `--ack-irreversible` when record deletions are requested.
- `create-zone` requires `--ack-irreversible` when the command would replace an existing DNS zone.
- Wix docs also note the broader Domain DNS family keeps up to 50 values per record type, and update methods are nameserver-gated for external domains connected by nameservers to Wix sites, not by pointing.
- This boundary is locally unit-tested and live-unverified.

## Read DNS propagation (account-level)

- `wix-safe-agent-cli dns-propagation get --dns-propagation-id <domain.tld>`

Notes for DNS propagation:
- This command uses account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`) and targets `GET /premium/domains/v1/dns-propagations/{dnsPropagationId}`.
- `--dns-propagation-id` is required. Wix docs describe it as the domain name including the TLD.
- Wix docs say propagation can take up to 48 hours and the response status can be `IN_PROGRESS`, `SUCCEEDED`, or `FAILED`.
- This boundary is locally unit-tested and live-unverified.

## Manage connected domains (account-level)

- `wix-safe-agent-cli connected-domains list [--limit N] [--cursor <cursor>]`
- `wix-safe-agent-cli connected-domains get --connected-domain-id <domain.tld>`
- `wix-safe-agent-cli connected-domains get-setup-info --connected-domain-id <domain.tld>`
- `wix-safe-agent-cli --plan-out plan.json connected-domains create --domain <domain.tld> --site-id <site_id> [--connection-type POINTING|NAMESERVERS|HIDDEN] [--assignment-type PRIMARY|REDIRECT] [--suppress-notifications]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json connected-domains create --domain <domain.tld> --site-id <site_id> --receipt-out receipt.json`
- `wix-safe-agent-cli --plan-out plan.json connected-domains delete --connected-domain-id <domain.tld>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json connected-domains delete --connected-domain-id <domain.tld> --receipt-out receipt.json`

Notes for Connected Domains:
- These commands use account-level auth (`WIX_API_KEY` + `WIX_ACCOUNT_ID`) and target:
  - `GET /domains/v1/connected-domains`
  - `GET /domains/v1/connected-domains/{connectedDomainId}`
  - `GET /domains/v1/connected-domain-setup-info/{connectedDomainId}`
  - `POST /domains/v1/connected-domains`
  - `DELETE /domains/v1/connected-domains/{connectedDomainId}`
- `connected-domains list` validates `--limit` in range 1-100 and rejects empty `--cursor`.
- `connected-domains get` and `connected-domains get-setup-info` require `--connected-domain-id`, enforce a TLD, and reject leading/trailing dots.
- `connected-domains create` is dry-run first, requires `--apply --yes`, supports `--plan-out`, `--plan-in`, and `--receipt-out`, and this tool requires `--site-id` so the target site is explicit and verifiable.
- `connected-domains create` adds `wix-site-id` on the live write request, preflights the target site through `sites query`, refuses if the domain already exists, and verifies success by reading the connected domain back.
- `connected-domains create` only proves that the connected-domain object was created. Wix docs say DNS changes can take up to 48 hours, so this boundary does not claim propagation is already complete.
- `connected-domains delete` is dry-run first, requires `--apply --yes --ack-irreversible`, supports `--plan-out`, `--plan-in`, and `--receipt-out`, snapshots the current connected-domain object, and verifies delete by expecting read-back `404`.
- Wix sample flows also note Premium-plan gating around real custom-domain connection paths, and delete can remove DNS records or make a site fall back to its free Wix URL.
- Official Wix docs and SDK examples show mixed auth examples for this family. This tool follows account-API-key headers (`Authorization` + `wix-account-id`) and stays explicit, with no generic request bridge.
- This boundary is locally unit-tested and live-unverified.

## Manage locations

- `wix-safe-agent-cli locations list [--include-archived] [--authorized-only] [--limit N] [--offset N] [--sort-field <field>] [--sort-order ASC|DESC]`
- `wix-safe-agent-cli locations query --query-json <query_json> [--authorized-only]`
- `wix-safe-agent-cli locations get --location-id <id>`
- `wix-safe-agent-cli locations create --location-json '<location_json>'`
- `wix-safe-agent-cli locations update --location-id <id> --location-json '<location_json>'`
- `wix-safe-agent-cli locations archive --location-id <id>`
- `wix-safe-agent-cli locations set-default --location-id <id>`

Notes for Locations:
- `locations` methods use the same app-token or stored-token auth path as the other site-context Business Management families in this tool.
- `locations list` and `locations query` support optional filtering and sort options.
- `locations create`, `locations update`, and `locations set-default` are dry-run first and use the reviewed-plan flow for live apply: `--plan-out`, then `--plan-in --apply --yes`.
- `locations update` is full-object replace-style and verifies by rereading the location.
- `locations archive` is write-only, requires `--plan-in --apply --yes --ack-irreversible`, and verifies success by rereading `archived=true`.
- This boundary is locally unit-tested and live-unverified.

## Manage tags

- `wix-safe-agent-cli tags list --fqdn <fqdn>`
- `wix-safe-agent-cli tags get --tag-id <id>`
- `wix-safe-agent-cli --plan-out plan.json tags create --tag-json '{"fqdn":"wix.ecom.v1.order","name":"VIP"}'`
- `wix-safe-agent-cli --plan-out plan.json tags update --tag-id <id> --tag-json '{"revision":"1","name":"VIP"}'`
- `wix-safe-agent-cli --plan-out plan.json tags delete --tag-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json tags create --tag-json '{"fqdn":"wix.ecom.v1.order","name":"VIP"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json tags update --tag-id <id> --tag-json '{"revision":"1","name":"VIP"}' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json tags delete --tag-id <id> [--receipt-out receipt.json]`

Notes for Tags:
- `tags` uses the same app-token or stored-token auth path as the other site-context Business Management families in this tool.
- `tags list` requires `--fqdn`. Official Wix docs currently say `list-tags` supports tags for the Orders FQDN `wix.ecom.v1.order`.
- `tags create`, `tags update`, and `tags delete` are all reviewed-plan writes in this tool.
- `tags create` preflights the current tag list for the target FQDN, refuses obvious duplicate names, and keeps the official `100`-tags-per-FQDN limit explicit.
- `tags update` requires `--tag-id` plus a payload with `revision` and `name`, preserves the current immutable `fqdn`, and verifies by rereading the tag.
- `tags delete` requires `--ack-irreversible` and verifies success by expecting `tags get` to return `404`.
- Tags receipts do not promise automatic rollback. They keep before-state availability and manual-only recovery notes explicit.
- This boundary is locally unit-tested and live-unverified.

## Manage site properties

- `wix-safe-agent-cli site-properties get [--field-path <path>]`
- `wix-safe-agent-cli --plan-out plan.json site-properties update-business-contact --contact-json '<contact_json>'`
- `wix-safe-agent-cli --plan-out plan.json site-properties update-business-profile --profile-json '<profile_json>'`
- `wix-safe-agent-cli --plan-out plan.json site-properties update-business-schedule --schedule-json '<schedule_json>'`
- `wix-safe-agent-cli --plan-out plan.json site-properties update-consent-policy --consent-json '<consent_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json site-properties update-business-contact --contact-json '<contact_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json site-properties update-business-profile --profile-json '<profile_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json site-properties update-business-schedule --schedule-json '<schedule_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json site-properties update-consent-policy --consent-json '<consent_json>'`

Notes for Site Properties:
- `site-properties get` reads properties for the installed site.
- All `site-properties` writes are plan-first.
- `site-properties` writes require a reviewed saved plan before live apply: `--plan-out`, then `--plan-in --apply --yes`.
- `site-properties` receipts verify by rereading targeted fields after apply.
- `update-business-schedule` is replacement-style for the full `businessSchedule` section and can overwrite existing values if omitted values are not included by caller payload.
- This boundary is locally unit-tested and live-unverified.

## Manage Cookie Consent Policy

- `wix-safe-agent-cli cookie-consent-policy get-cookie-banner-settings [--language-code en]`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy update-cookie-banner-settings --settings-json '<settings_json>'`
- `wix-safe-agent-cli cookie-consent-policy get-cmp-config`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy update-cmp-config --cmp-config-json '<cmp_config_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy create-consent-config --consent-config-json '<consent_config_json>'`
- `wix-safe-agent-cli cookie-consent-policy get-consent-config --consent-config-id <id>`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy update-consent-config --consent-config-json '<consent_config_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy delete-consent-config --consent-config-id <id>`
- `wix-safe-agent-cli cookie-consent-policy query-consent-configs --query-json '<query_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy bulk-create-consent-configs --bulk-json '<bulk_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy bulk-delete-consent-configs --bulk-json '<bulk_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy bulk-update-consent-configs --bulk-json '<bulk_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy bulk-update-consent-config-tags --tags-json '<tags_json>'`
- `wix-safe-agent-cli --plan-out plan.json cookie-consent-policy bulk-update-consent-config-tags-by-filter --tags-json '<tags_json>'`
- `wix-safe-agent-cli cookie-consent-policy list-apps-and-storage --query-json '{}'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json cookie-consent-policy update-cookie-banner-settings --settings-json '<settings_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json cookie-consent-policy update-cmp-config --cmp-config-json '<cmp_config_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json cookie-consent-policy update-consent-config --consent-config-json '<consent_config_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json cookie-consent-policy delete-consent-config --consent-config-id <id> [--receipt-out receipt.json]`

Notes for Cookie Consent Policy:
- This is a separate official family from `site-properties update-consent-policy`.
- Reads are `get-cookie-banner-settings`, `get-cmp-config`, `get-consent-config`, `query-consent-configs`, and `list-apps-and-storage`.
- Writes are plan-first. Use `--plan-out`, review the plan, then use `--plan-in --apply --yes`.
- `delete-consent-config`, `bulk-delete-consent-configs`, and `bulk-update-consent-config-tags-by-filter` also require `--ack-irreversible`.
- `update-consent-config` requires `consentConfig.id` and `consentConfig.revision`.
- Wix marks `bulk-update-consent-configs` as Developer Preview.
- Consent Config Created, Deleted, and Updated are callback-only events and are not CLI commands.
- This boundary is locally unit-tested and live-unverified.

## Manage dashboard favorite list

- `wix-safe-agent-cli dashboard-favorite-list get`
- `wix-safe-agent-cli --plan-out plan.json dashboard-favorite-list create --favorite-list-json '<favorite_list_json>'`
- `wix-safe-agent-cli --plan-out plan.json dashboard-favorite-list update --favorite-list-json '<favorite_list_json>'`
- `wix-safe-agent-cli --plan-out plan.json dashboard-favorite-list delete --favorite-list-id <id>`
- `wix-safe-agent-cli --plan-out plan.json dashboard-favorite-list add-favorite --favorite-json '<favorite_json>'`
- `wix-safe-agent-cli --plan-out plan.json dashboard-favorite-list delete-favorite --favorite-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json dashboard-favorite-list create --favorite-list-json '<favorite_list_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json dashboard-favorite-list update --favorite-list-json '<favorite_list_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json dashboard-favorite-list delete --favorite-list-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json dashboard-favorite-list add-favorite --favorite-json '<favorite_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json dashboard-favorite-list delete-favorite --favorite-id <id> [--receipt-out receipt.json]`

### FAQ App: Category V2

- `wix-safe-agent-cli faq-category-v2 list`
- `wix-safe-agent-cli faq-category-v2 get --category-id <id>`
- `wix-safe-agent-cli faq-category-v2 query --query-json '<query_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-category-v2 create --category-json '<category_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-category-v2 update --category-json '<category_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-category-v2 delete --category-id <id>`
- `wix-safe-agent-cli --plan-out plan.json faq-category-v2 update-extended-fields --category-id <id> --extended-fields-json '<extended_fields_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-category-v2 create --category-json '<category_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-category-v2 update --category-json '<category_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json faq-category-v2 delete --category-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-category-v2 update-extended-fields --category-id <id> --extended-fields-json '<extended_fields_json>' [--receipt-out receipt.json]`

### FAQ App: Question Entry V2

- `wix-safe-agent-cli faq-question-entry-v2 list`
- `wix-safe-agent-cli faq-question-entry-v2 get --question-entry-id <id>`
- `wix-safe-agent-cli faq-question-entry-v2 query --query-json '<query_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 create --question-entry-json '<question_entry_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 update --question-entry-json '<question_entry_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 delete --question-entry-id <id>`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 bulk-delete --question-entries-json '<question_entries_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 bulk-update --question-entries-json '<question_entries_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 set-labels --question-entry-id <id> --labels-json '<labels_json>'`
- `wix-safe-agent-cli --plan-out plan.json faq-question-entry-v2 update-extended-fields --question-entry-id <id> --extended-fields-json '<extended_fields_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-question-entry-v2 create --question-entry-json '<question_entry_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-question-entry-v2 update --question-entry-json '<question_entry_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json faq-question-entry-v2 delete --question-entry-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json faq-question-entry-v2 bulk-delete --question-entries-json '<question_entries_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-question-entry-v2 bulk-update --question-entries-json '<question_entries_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-question-entry-v2 set-labels --question-entry-id <id> --labels-json '<labels_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json faq-question-entry-v2 update-extended-fields --question-entry-id <id> --extended-fields-json '<extended_fields_json>' [--receipt-out receipt.json]`

### Functions: Functions V1

- `wix-safe-agent-cli functions-v1 get --function-id <id>`
- `wix-safe-agent-cli functions-v1 query --query-json '<query_json>'`
- `wix-safe-agent-cli --plan-out plan.json functions-v1 create --function-json '<function_json>'`
- `wix-safe-agent-cli --plan-out plan.json functions-v1 update --function-json '<function_json>'`
- `wix-safe-agent-cli --plan-out plan.json functions-v1 delete --function-id <id>`
- `wix-safe-agent-cli --plan-out plan.json functions-v1 bulk-update-tags --tags-json '<tags_json>'`
- `wix-safe-agent-cli --plan-out plan.json functions-v1 bulk-update-tags-by-filter --tags-json '<tags_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json functions-v1 create --function-json '<function_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json functions-v1 update --function-json '<function_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json functions-v1 delete --function-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json functions-v1 bulk-update-tags --tags-json '<tags_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json functions-v1 bulk-update-tags-by-filter --tags-json '<tags_json>' [--receipt-out receipt.json]`

Notes for Functions V1:
- `functions-v1 get` and `query` inspect function objects.
- Writes are plan-first. Use `--plan-out`, review the plan, then use `--plan-in --apply --yes`.
- `update` requires `function.id` and the current `function.revision`.
- `delete` also requires `--ack-irreversible` because Wix says deletion permanently removes the function from the site's dashboard Function List.
- `bulk-update-tags-by-filter` also requires `--ack-irreversible` because Wix says an empty filter updates all functions.
- Function Created, Deleted, Tags Modified, and Updated are callback-only events and are not CLI commands.
- Wix says creating a function directly is not the recommended full creation path because logic, methods, and service-plugin configuration are managed by other Functions APIs.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function Types

- `wix-safe-agent-cli function-types get --app-def-id <app_def_id> --function-type-id <function_type_id>`
- `wix-safe-agent-cli function-types query --query-json '<query_json>'`

Notes for Function Types:
- This is a read-only Functions subfamily.
- `function-types get` retrieves one function type by app definition ID and function type ID.
- `function-types query` retrieves available function types. Wix defaults to `paging.limit` 50 and `paging.offset` 0.
- Official docs say query does not support filters or sorting.
- Function types are provided by installed business solutions and are available only when the relevant business solution is installed on the site.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function Templates

- `wix-safe-agent-cli function-templates get --app-def-id <app_def_id> --function-template-id <function_template_id>`
- `wix-safe-agent-cli function-templates query --query-json '<query_json>'`

Notes for Function Templates:
- This is a read-only Functions subfamily.
- `function-templates get` retrieves one function template by app definition ID and function template ID.
- `function-templates query` retrieves available templates. Wix says `appDefId` and `functionExtensionId` are required filters.
- Query defaults to `paging.limit` 50 and `paging.offset` 0.
- Function templates are drafts for basic or builderless function creation. Builderless creation requires a template with `formTemplateExtensionId`.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function Productions

- `wix-safe-agent-cli --plan-out plan.json function-productions create --production-json '<production_json>'`
- `wix-safe-agent-cli --plan-out plan.json function-productions update --production-json '<production_json>'`
- `wix-safe-agent-cli --plan-out plan.json function-productions delete --function-production-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json function-productions create --production-json '<production_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json function-productions update --production-json '<production_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json function-productions delete --function-production-id <id> [--receipt-out receipt.json]`

Notes for Function Productions:
- This is a write-only Functions subfamily.
- `function-productions create` creates a function, automation, service plugin configuration, and function method in one call.
- `function-productions update` updates a function production and requires `functionProduction.id` in `--production-json`.
- `function-productions delete` deletes the production and all associated entities, so apply requires `--ack-irreversible`.
- Wix says templates with `formTemplateExtensionId` cannot use Function Productions and must use Builderless Productions instead.
- This boundary is locally unit-tested and live-unverified.

### Functions: Builderless Productions

- `wix-safe-agent-cli --plan-out plan.json builderless-productions create --builderless-production-json '<builderless_production_json>'`
- `wix-safe-agent-cli builderless-productions get --function-id <function_id>`
- `wix-safe-agent-cli --plan-out plan.json builderless-productions update --builderless-production-json '<builderless_production_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json builderless-productions create --builderless-production-json '<builderless_production_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json builderless-productions update --builderless-production-json '<builderless_production_json>' [--receipt-out receipt.json]`

Notes for Builderless Productions:
- `builderless-productions create` creates a ready-to-activate function, automation, service plugin configuration, and function method from a template with `formTemplateExtensionId`.
- `builderless-productions get` retrieves one builderless production by `functionId`.
- `builderless-productions update` updates a builderless production and requires `functionBuilderlessProduction.id` in `--builderless-production-json`.
- Wix says to retrieve required form fields through Form Schema List Forms with namespace `wix.function_template.form`, the template form ID, and kind `EXTENSION`.
- Wix says update may have no effect after related elements are updated through other APIs and the builderless production object becomes out of date.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function Methods

- `wix-safe-agent-cli --plan-out plan.json function-methods create --function-method-json '<function_method_json>'`
- `wix-safe-agent-cli --plan-out plan.json function-methods delete --function-method-id <id>`
- `wix-safe-agent-cli function-methods query [--query-json '<query_json>']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json function-methods create --function-method-json '<function_method_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json function-methods delete --function-method-id <id> [--receipt-out receipt.json]`

Notes for Function Methods:
- `function-methods create` creates a function method link between a function and an automation.
- Wix says creating function methods directly is not the recommended full creation path. Use Function Productions or Builderless Productions for full function creation.
- `function-methods query` retrieves function methods. Wix says the default sort is `createdDate DESC`, with `paging.limit` 50 and `paging.offset` 0.
- Query filters and sorting are documented for `id`, `functionId`, and `automationId`.
- `function-methods delete` deletes a function method link and requires `--ack-irreversible` on apply.
- Function Method Created and Function Method Deleted are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function Activations

- `wix-safe-agent-cli --plan-out plan.json function-activations upsert --activation-json '<activation_json>'`
- `wix-safe-agent-cli --plan-out plan.json function-activations delete --function-id <function_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json function-activations upsert --activation-json '<activation_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json function-activations delete --function-id <function_id> [--receipt-out receipt.json]`

Notes for Function Activations:
- `function-activations upsert` activates a draft function or reactivates an active function so the latest changes go live.
- Wix says a no-change reactivation still updates the function activation object's revision.
- `function-activations delete` deactivates the function and sets activation status to `INACTIVE`.
- Both commands are reviewed-plan writes and require `--ack-irreversible` because they change whether business solutions can execute the function.
- This boundary is locally unit-tested and live-unverified.

### Functions: Function SPI Configurations

- `wix-safe-agent-cli --plan-out plan.json function-spi-configurations create --spi-configuration-json '<spi_configuration_json>'`
- `wix-safe-agent-cli function-spi-configurations get --spi-configuration-id <id>`
- `wix-safe-agent-cli --plan-out plan.json function-spi-configurations update --spi-configuration-json '<spi_configuration_json>'`
- `wix-safe-agent-cli --plan-out plan.json function-spi-configurations delete --spi-configuration-id <id>`
- `wix-safe-agent-cli function-spi-configurations query [--query-json '<query_json>']`
- `wix-safe-agent-cli function-spi-configurations validate --spi-configuration-json '<spi_configuration_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json function-spi-configurations create --spi-configuration-json '<spi_configuration_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json function-spi-configurations update --spi-configuration-json '<spi_configuration_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json function-spi-configurations delete --spi-configuration-id <id> [--receipt-out receipt.json]`

Notes for Function SPI Configurations:
- `function-spi-configurations create` creates service plugin configuration data for a function.
- `function-spi-configurations get` reads one configuration by ID.
- `function-spi-configurations update` updates a configuration and requires `functionSpiConfiguration.id` and current `functionSpiConfiguration.revision`.
- Wix says configuration updates do not affect active functions until the function is reactivated with Function Activations.
- `function-spi-configurations delete` deletes a configuration and requires `--ack-irreversible` on apply.
- `function-spi-configurations query` retrieves configurations and defaults to `createdDate DESC`, `paging.limit` 50, and `paging.offset` 0.
- Query filters and sorting are documented for `id` and `functionId`.
- `function-spi-configurations validate` checks a configuration against the service plugin schema without creating it.
- SPI Configuration Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Payment Link Settings

- `wix-safe-agent-cli payment-link-settings get`
- `wix-safe-agent-cli --plan-out plan.json payment-link-settings update --settings-json '<settings_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-link-settings update --settings-json '<settings_json>' [--receipt-out receipt.json]`

Notes for Payment Link Settings:
- `payment-link-settings get` reads the current site's payment link checkout settings.
- `payment-link-settings update` updates payment link checkout settings and is always reviewed-plan first.
- Apply requires `--plan-in --apply --yes`; no destructive acknowledgement is required.
- Verification is the provider response plus a follow-up `payment-link-settings get`.
- Bulk Downloads is tracked separately as Developer Preview, so this stable CLI does not expose Bulk Downloads commands yet.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Billable Items

- `wix-safe-agent-cli --plan-out plan.json billable-items create --billable-item-json '<billable_item_json>'`
- `wix-safe-agent-cli billable-items get --billable-item-id <id>`
- `wix-safe-agent-cli --plan-out plan.json billable-items update --billable-item-json '<billable_item_json>'`
- `wix-safe-agent-cli --plan-out plan.json billable-items delete --billable-item-id <id>`
- `wix-safe-agent-cli billable-items query [--query-json '<query_json>']`
- `wix-safe-agent-cli billable-items search [--search-json '<search_json>']`
- `wix-safe-agent-cli --plan-out plan.json billable-items bulk-create --billable-items-json '<billable_items_json>'`
- `wix-safe-agent-cli --plan-out plan.json billable-items bulk-delete --billable-items-json '<billable_items_json>'`
- `wix-safe-agent-cli --plan-out plan.json billable-items bulk-update --billable-items-json '<billable_items_json>'`
- `wix-safe-agent-cli --plan-out plan.json billable-items bulk-update-tags --tags-json '<tags_json>'`
- `wix-safe-agent-cli --plan-out plan.json billable-items bulk-update-tags-by-filter --tags-json '<tags_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json billable-items create --billable-item-json '<billable_item_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json billable-items update --billable-item-json '<billable_item_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json billable-items delete --billable-item-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json billable-items bulk-create --billable-items-json '<billable_items_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json billable-items bulk-delete --billable-items-json '<billable_items_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json billable-items bulk-update --billable-items-json '<billable_items_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json billable-items bulk-update-tags --tags-json '<tags_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json billable-items bulk-update-tags-by-filter --tags-json '<tags_json>' [--receipt-out receipt.json]`

Notes for Billable Items:
- `billable-items get`, `query`, and `search` are reads/helpers. Wix marks `search` Developer Preview.
- `billable-items create`, `bulk-create`, `update`, `bulk-update`, `bulk-update-tags`, and `bulk-update-tags-by-filter` are reviewed-plan writes.
- Wix marks `create` and `bulk-update` Developer Preview.
- `billable-items update` requires `billableItem.id` and current `billableItem.revision`.
- `billable-items delete` and `bulk-delete` require `--ack-irreversible`.
- `billable-items bulk-update-tags-by-filter` is async and requires `--ack-irreversible` because an empty filter updates all billable items.
- Billable Item Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Payment Links

- `wix-safe-agent-cli --plan-out plan.json payment-links create --payment-link-json '<payment_link_json>'`
- `wix-safe-agent-cli payment-links get --payment-link-id <id>`
- `wix-safe-agent-cli --plan-out plan.json payment-links delete --payment-link-id <id>`
- `wix-safe-agent-cli payment-links query [--query-json '<query_json>']`
- `wix-safe-agent-cli payment-links search [--search-json '<search_json>']`
- `wix-safe-agent-cli --plan-out plan.json payment-links activate --payment-link-id <id>`
- `wix-safe-agent-cli --plan-out plan.json payment-links deactivate --payment-link-id <id>`
- `wix-safe-agent-cli --plan-out plan.json payment-links initiate-payment --payment-link-id <id>`
- `wix-safe-agent-cli --plan-out plan.json payment-links send --payment-link-id <id> --send-json '<send_json>'`
- `wix-safe-agent-cli --plan-out plan.json payment-links set-note --payment-link-id <id> --note-json '<note_json>'`
- `wix-safe-agent-cli --plan-out plan.json payment-links update-extended-fields --payment-link-id <id> --extended-fields-json '<extended_fields_json>'`
- `wix-safe-agent-cli --plan-out plan.json payment-links bulk-update-tags --tags-json '<tags_json>'`
- `wix-safe-agent-cli --plan-out plan.json payment-links bulk-update-tags-by-filter --tags-json '<tags_json>'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links create --payment-link-json '<payment_link_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links delete --payment-link-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links activate --payment-link-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links deactivate --payment-link-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-links initiate-payment --payment-link-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links send --payment-link-id <id> --send-json '<send_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-links set-note --payment-link-id <id> --note-json '<note_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-links update-extended-fields --payment-link-id <id> --extended-fields-json '<extended_fields_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-links bulk-update-tags --tags-json '<tags_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json payment-links bulk-update-tags-by-filter --tags-json '<tags_json>' [--receipt-out receipt.json]`

Notes for Payment Links:
- `payment-links get`, `query`, and `search` are reads/helpers.
- `payment-links create`, `delete`, `activate`, `deactivate`, `initiate-payment`, `send`, `set-note`, `update-extended-fields`, `bulk-update-tags`, and `bulk-update-tags-by-filter` are reviewed-plan writes.
- `payment-links create` requires `--ack-irreversible` because Wix says settings such as price value and payment limit cannot be changed after creation.
- `payment-links delete`, `activate`, `deactivate`, and `send` require `--ack-irreversible`; delete cannot be used after funds are received, activate/deactivate changes payment acceptance, and send can notify up to 50 recipients.
- `payment-links bulk-update-tags-by-filter` is async and requires `--ack-irreversible` because an empty filter updates all payment links.
- `payment-links initiate-payment` creates a Wix eCommerce checkout and is intended for in-person Wix user checkout flows rather than the standard payment link flow.
- Payment Link Created, Deleted, Activated, Deactivated, Note Set, Payment Initiated, Sent, and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Payment Link Payments

- `wix-safe-agent-cli payment-link-payments query [--query-json '<query_json>']`
- `wix-safe-agent-cli payment-link-payments search [--search-json '<search_json>']`
- `wix-safe-agent-cli --plan-out plan.json payment-link-payments issue-receipt --payment-link-payment-id <id>`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json payment-link-payments issue-receipt --payment-link-payment-id <id> [--receipt-out receipt.json]`

Notes for Payment Link Payments:
- `payment-link-payments query` and `search` are reads/helpers for payment records created from payment links.
- `payment-link-payments issue-receipt` is a reviewed-plan write because it creates a Get Paid receipt for the selected payment link payment.
- Verify receipt issuing by inspecting the provider response, then rerunning `payment-link-payments query` or `search` and checking the payment's `receiptId`.
- Payment Link Payment Created and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Receipts

- `wix-safe-agent-cli --plan-out plan.json receipts create --receipt-json '<receipt_json>'`
- `wix-safe-agent-cli receipts get --receipt-id <id>`
- `wix-safe-agent-cli receipts query [--query-json '<query_json>']`
- `wix-safe-agent-cli receipts get-latest-number [--prefix <prefix>]`
- `wix-safe-agent-cli --plan-out plan.json receipts regenerate-document --receipt-id <id>`
- `wix-safe-agent-cli --plan-out plan.json receipts send-email --receipt-id <id> [--send-json '<send_json>']`
- `wix-safe-agent-cli --plan-out plan.json receipts update-extended-fields --receipt-id <id> --extended-fields-json '<extended_fields_json>'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json receipts create --receipt-json '<receipt_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipts regenerate-document --receipt-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json receipts send-email --receipt-id <id> [--send-json '<send_json>'] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipts update-extended-fields --receipt-id <id> --extended-fields-json '<extended_fields_json>' [--receipt-out receipt.json]`

Notes for Receipts:
- `receipts get`, `query`, and `get-latest-number` are reads/helpers. `get-latest-number` accepts optional `--prefix`.
- `receipts create`, `regenerate-document`, `send-email`, and `update-extended-fields` are reviewed-plan writes.
- `receipts create` requires `--ack-irreversible` because Wix says receipts can be created but not deleted, and only one receipt can be created for each transaction.
- `receipts send-email` requires `--ack-irreversible` because it sends receipt email to the customer.
- `receipts regenerate-document` is intended for failed or stuck receipt documents.
- `receipts update-extended-fields` updates custom fields only and does not increment revision.
- Receipt Created, Sent, and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Get Paid: Receipt Presets

- `wix-safe-agent-cli --plan-out plan.json receipt-presets create --receipt-preset-json '<receipt_preset_json>'`
- `wix-safe-agent-cli receipt-presets get --receipt-preset-id <id>`
- `wix-safe-agent-cli --plan-out plan.json receipt-presets update --receipt-preset-json '<receipt_preset_json>'`
- `wix-safe-agent-cli --plan-out plan.json receipt-presets delete --receipt-preset-id <id>`
- `wix-safe-agent-cli receipt-presets list`
- `wix-safe-agent-cli receipt-presets get-default`
- `wix-safe-agent-cli --plan-out plan.json receipt-presets set-default --receipt-preset-id <id>`
- `wix-safe-agent-cli --plan-out plan.json receipt-presets update-extended-fields --receipt-preset-id <id> --extended-fields-json '<extended_fields_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipt-presets create --receipt-preset-json '<receipt_preset_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipt-presets update --receipt-preset-json '<receipt_preset_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json receipt-presets delete --receipt-preset-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipt-presets set-default --receipt-preset-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipt-presets update-extended-fields --receipt-preset-id <id> --extended-fields-json '<extended_fields_json>' [--receipt-out receipt.json]`

Notes for Receipt Presets:
- `receipt-presets get`, `list`, and `get-default` are reads/helpers.
- `receipt-presets create`, `update`, `delete`, `set-default`, and `update-extended-fields` are reviewed-plan writes.
- `receipt-presets update` requires `receiptPreset.id` and current `receiptPreset.revision`.
- `receipt-presets delete` requires `--ack-irreversible` because it permanently deletes the preset.
- `receipt-presets set-default` affects which preset is used during future receipt creation when no preset is specified or found.
- `receipt-presets update-extended-fields` updates custom fields only and does not increment revision.

### Get Paid: Receipts Settings

- `wix-safe-agent-cli receipts-settings get`
- `wix-safe-agent-cli --plan-out plan.json receipts-settings update --settings-json '<settings_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json receipts-settings update --settings-json '<settings_json>' [--receipt-out receipt.json]`

Notes for Receipts Settings:
- `receipts-settings get` reads the site's receipt numbering settings.
- `receipts-settings update` updates receipt numbering settings and is always reviewed-plan first.
- `receipts-settings update` requires current `receiptsSettings.revision`.
- Verification is the provider response plus a follow-up `receipts-settings get`.

### Headless: OAuth Apps

- `wix-safe-agent-cli --plan-out plan.json headless-oauth-apps create --o-auth-app-json '<o_auth_app_json>'`
- `wix-safe-agent-cli headless-oauth-apps get --o-auth-app-id <id>`
- `wix-safe-agent-cli --plan-out plan.json headless-oauth-apps update --o-auth-app-json '<o_auth_app_json>'`
- `wix-safe-agent-cli headless-oauth-apps query --query-json '<query_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json headless-oauth-apps create --o-auth-app-json '<o_auth_app_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json headless-oauth-apps update --o-auth-app-json '<o_auth_app_json>' [--receipt-out receipt.json]`

Notes for Headless OAuth Apps:
- `headless-oauth-apps get` reads one OAuth app by ID.
- `headless-oauth-apps query` retrieves OAuth apps by Wix query payload; it is a read/helper even though the official endpoint uses `POST`.
- `headless-oauth-apps create` and `update` are reviewed-plan writes because OAuth apps authorize external clients to authenticate with a Wix Headless project or site.
- `headless-oauth-apps update` requires `oAuthApp.id` and `mask.paths`; Wix only updates fields named in `mask.paths`.
- OAuth App Created, Deleted, and Updated are webhook/event surfaces, not CLI commands.
- This boundary is locally unit-tested and live-unverified.

### Headless: Authentication

- `wix-safe-agent-cli headless-authentication login-v2 --login-json '<login_json>'`
- `wix-safe-agent-cli headless-authentication retrieve-tokens --token-json '<token_json>'`
- `wix-safe-agent-cli --plan-out plan.json headless-authentication register-v2 --register-json '<register_json>'`
- `wix-safe-agent-cli --plan-out plan.json headless-authentication change-password --password-json '<password_json>'`
- `wix-safe-agent-cli --plan-out plan.json headless-authentication logout [--params-json '<params_json>']`
- `wix-safe-agent-cli --plan-out plan.json headless-authentication sign-on --sign-on-json '<sign_on_json>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json headless-authentication register-v2 --register-json '<register_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json headless-authentication change-password --password-json '<password_json>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json headless-authentication logout [--params-json '<params_json>'] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json headless-authentication sign-on --sign-on-json '<sign_on_json>' [--receipt-out receipt.json]`

Notes for Headless Authentication:
- `login-v2` logs in an existing member and returns a redacted response; password and session token fields are never printed.
- `retrieve-tokens` calls the OAuth token endpoint with a JSON request and redacts authorization code, code verifier, refresh token, access token, and refresh token values.
- `register-v2` can register a member or trigger email verification for an existing contact email, so it stays reviewed-plan first.
- `change-password` changes logged-in member credentials and requires `--ack-irreversible`.
- `logout` terminates a member session and may return redacted cookie headers.
- `sign-on` is for trusted integrations with verified user information, may create or update a member account, and requires `--ack-irreversible`.
- Wix currently marks `retrieve-tokens`, `change-password`, `logout`, and `sign-on` Developer Preview.
- Password, token, code, cookie, and session token fields are redacted from command output, plans, receipts, and audit payloads.
- This boundary is locally unit-tested and live-unverified.

### Headless: Recovery

- `wix-safe-agent-cli --plan-out plan.json headless-recovery send-recovery-email --recovery-json '<recovery_json>'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json headless-recovery send-recovery-email --recovery-json '<recovery_json>' [--receipt-out receipt.json]`

Notes for Headless Recovery:
- `send-recovery-email` sends a member a Wix-managed password-reset email, so it is reviewed-plan first and apply requires `--ack-irreversible`.
- Use the official request body with `--recovery-json` or `--recovery-json @request.json`.
- Official docs say the connected Wix site must be published before recovery email flows work.
- Official docs say redirect URLs used after password change must be added as allowed authorization redirect URIs.
- Provider response proves Wix accepted the request, but it does not prove inbox delivery or password reset completion.
- This boundary is locally unit-tested and live-unverified.

### Headless: Redirects

- `wix-safe-agent-cli --plan-out plan.json headless-redirects create-redirect-session --redirect-session-json '<redirect_session_json>'`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json headless-redirects create-redirect-session --redirect-session-json '<redirect_session_json>' [--receipt-out receipt.json]`

Notes for Headless Redirects:
- `create-redirect-session` creates a single-use URL for redirecting a visitor to a Wix-managed page for authentication, logout, checkout, product, or booking flows.
- Use the official request body with `--redirect-session-json` or `--redirect-session-json @request.json`.
- The command requires exactly one official redirect intent in the request body, such as `auth`, `login`, `logout`, `ecomCheckout`, `eventsCheckout`, `paidPlansCheckout`, `bookingsCheckout`, `storesProduct`, or `bookingsBook`.
- This command is reviewed-plan first and apply requires `--ack-irreversible` because it creates a live visitor-flow URL.
- Official docs say allowed redirect domains and allowed authorization redirect URIs must be configured in Headless Settings, and the connected Wix site must be published.
- The official docs currently disagree on the endpoint path: the rendered method page shows `/_api/redirects-api/v1/redirect-session`, the generated REST schema shows `/headless/v1/redirect-session`, and the official REST guide plus method curl example show `/redirect-session/v1/redirect-session`. This command follows the rendered method page path.
- `sessionToken` fields are redacted from output, plans, receipts, and audit payloads, while the returned redirect URL is preserved because it is the command's intended result.
- Redirect Session Created is a webhook/event surface, not a CLI command.
- This boundary is locally unit-tested and live-unverified.

### Headless: Sitemap

- `wix-safe-agent-cli headless-sitemap list-pages [--item-type BLOG_POST] [--limit 50] [--cursor '<cursor>']`

Notes for Headless Sitemap:
- `list-pages` is read-only and lists sitemap entries for an official Headless item type.
- `--item-type` is optional in the official schema. When supplied, it must be one of the official enum values such as `BLOG_POST`, `STORES_PRODUCT`, `BOOKINGS_SERVICE`, `EVENTS_PAGE`, `PORTFOLIO_PROJECTS`, `PRICING_PLANS`, or `RESTAURANTS_MENU_PAGE`.
- `--limit` maps to the official cursor-paging limit and must be between 0 and 200.
- `--cursor` passes the next or previous cursor from `pagingMetadata.cursors`.
- The official docs currently disagree on the endpoint path: the rendered method page and embedded schema show `/v1/list-sitemap-pages`, while the official curl example shows `/seo/v1/headless-sitemap/pages`. This command follows the rendered method page and embedded schema path.
- This boundary is locally unit-tested and live-unverified.

### Headless: Verification

- `wix-safe-agent-cli --plan-out plan.json headless-verification verify-during-authentication --code 123456 --state-token '<state-token>'`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json headless-verification verify-during-authentication --code 123456 --state-token '<state-token>' [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json headless-verification verify-during-authentication --verification-json @verify.json`

Notes for Headless Verification:
- `verify-during-authentication` is the official Developer Preview method for continuing an auth flow that returned `REQUIRE_EMAIL_VERIFICATION`.
- Use `--code` and `--state-token`, or pass the official body with `--verification-json`.
- The command is reviewed-plan first because it can complete a member registration/authentication step. Apply requires `--plan-in --apply --yes`.
- `code`, `stateToken`, `sessionToken`, access token, and refresh token fields are redacted from output, plans, receipts, and audit payloads.
- Provider response can return `SUCCESS` and a redacted `sessionToken`, or another auth state. Use `headless-authentication retrieve-tokens` separately after successful verification when tokens are needed.
- The official docs currently disagree on the endpoint path: the rendered method page and official curl example show `/_api/iam/verification/v1/auth/verify`, while the generated markdown schema shows `/v1/auth/verify`. This command follows the rendered method page path.
- This boundary is locally unit-tested and live-unverified.

Notes for Dashboard Favorite List:
- This is the callable Dashboard API subfamily in the current official Wix docs.
- `dashboard-favorite-list get` reads the current Wix user's dashboard favorite list.
- Writes are plan-first. Use `--plan-out`, review the plan, then use `--plan-in --apply --yes`.
- `update` requires `favoriteList.id` and the current `favoriteList.revision`, and official docs say update replaces the list contents.
- `delete` and `delete-favorite` also require `--ack-irreversible`; `delete-favorite` can delete the list when no favorites remain.
- Official docs say each Wix user can have only one list and recommend changing it only after explicit user action.
- Favorite List Created, Deleted, and Updated are callback-only events and are not CLI commands.
- This boundary is locally unit-tested and live-unverified.

## Multilingual locale settings

Commands:

- `wix-safe-agent-cli multilingual-locale-settings get`
- `wix-safe-agent-cli multilingual-locale-settings set-mode --enabled true`
- `wix-safe-agent-cli multilingual-locale-settings set-mode --enabled false`
- `wix-safe-agent-cli multilingual-locale-settings update --locale-settings-json '{"revision":"1","autoSwitch":true}'`

Notes for Multilingual locale settings:

- The Wix Multilingual app must be installed on the site.
- `get` maps to `GET /locale-settings/v2/settings`.
- `set-mode` maps to `POST /locale-settings/v2/settings/mode`.
- `update` maps to `PATCH /locale-settings/v2/settings` and requires the current `localeSettings.revision`.
- Do not use `update` to change multilingual mode; use `set-mode`.
- Writes are dry-run first and support `--plan-out`, `--plan-in`, `--apply`, `--yes`, and `--receipt-out`.
- Disabling multilingual mode removes translated content and resets locale settings, so `set-mode --enabled false` requires `--ack-irreversible` for live apply.

## Multilingual locales

Commands:

- `wix-safe-agent-cli multilingual-locales create --locale-json '{"languageCode":"fr","regionCode":"FR"}'`
- `wix-safe-agent-cli multilingual-locales get --locale-id fr-FR`
- `wix-safe-agent-cli multilingual-locales update --locale-json '{"id":"fr-FR","revision":"1","visibility":"VISIBLE"}'`
- `wix-safe-agent-cli multilingual-locales delete --locale-id fr-FR`
- `wix-safe-agent-cli multilingual-locales query --filter-json '{"visibility":{"$eq":"VISIBLE"}}' --limit 100`
- `wix-safe-agent-cli multilingual-locales bulk-create --locales-json '[{"languageCode":"fr","regionCode":"FR"}]'`
- `wix-safe-agent-cli multilingual-locales bulk-delete --locale-ids-json '["fr-FR"]'`
- `wix-safe-agent-cli multilingual-locales bulk-update --locales-json '[{"locale":{"id":"fr-FR","revision":"1","visibility":"VISIBLE"}}]'`
- `wix-safe-agent-cli multilingual-locales create-new-primary --primary-locale-json '{"languageCode":"en","regionCode":"US"}'`
- `wix-safe-agent-cli multilingual-locales get-new-primary-status --token <token>`
- `wix-safe-agent-cli multilingual-locales list-supported --language-code fr`
- `wix-safe-agent-cli multilingual-locales set-visitor-primary --locale-id fr-FR`

Notes for Multilingual locales:

- The Wix Multilingual app must be installed, and multilingual mode must be enabled before creating secondary locales.
- `create` maps to `POST /locales/v2/locale`.
- `get` maps to `GET /locales/v2/locale/{localeId}`.
- `update` maps to `PATCH /locales/v2/locale/{locale.id}` and requires the current locale revision.
- `delete` maps to `DELETE /locales/v2/locale/{localeId}` and only deletes secondary locales.
- `query` maps to `POST /locales/v2/locale/query`; `--limit` is capped at 100.
- `bulk-create`, `bulk-delete`, and `bulk-update` use the official bulk locale routes and accept up to 100 items.
- `create-new-primary` maps to `POST /locales/v2/locale/change-primary` and returns a token for status checks.
- `get-new-primary-status` maps to `GET /locales/v2/locale/change-primary?token=...`.
- `list-supported` maps to `GET /locales/v2/locales/supported`.
- `set-visitor-primary` maps to `POST /locales/v2/locale/set-visitor-primary`; Wix says the locale must be visible.
- Writes are dry-run first and support `--plan-out`, `--plan-in`, `--apply`, `--yes`, and `--receipt-out`.
- `delete`, `bulk-delete`, and `create-new-primary` require `--ack-irreversible` for live apply.

## Multilingual translation schemas

Commands:

- `wix-safe-agent-cli multilingual-translation-schemas create --schema-json '{"key":{"entityType":"post","scope":"SITE"},"fields":{"title":{"type":"SHORT_TEXT"}}}'`
- `wix-safe-agent-cli multilingual-translation-schemas get --schema-id <schema-id>`
- `wix-safe-agent-cli multilingual-translation-schemas update --schema-json '{"id":"<schema-id>","revision":"1","displayName":"Blog post"}'`
- `wix-safe-agent-cli multilingual-translation-schemas delete --schema-id <schema-id>`
- `wix-safe-agent-cli multilingual-translation-schemas query --filter-json '{"key.scope":{"$eq":"SITE"}}' --limit 100`
- `wix-safe-agent-cli multilingual-translation-schemas list-site --app-id <app-id> --entity-type post --scope SITE --limit 100`
- `wix-safe-agent-cli multilingual-translation-schemas get-by-key --app-id <app-id> --entity-type post --scope SITE`

Notes for Multilingual translation schemas:

- The Wix Multilingual app must be installed on the site.
- `create` maps to `POST /translation-schema/v1/schemas`.
- `get` maps to `GET /translation-schema/v1/schemas/{schemaId}`.
- `update` maps to `PATCH /translation-schema/v1/schemas/{schema.id}` and requires the current schema revision.
- `delete` maps to `DELETE /translation-schema/v1/schemas/{schemaId}`.
- `query` maps to `POST /translation-schema/v1/schemas/query`; `--limit` is capped at 100.
- `list-site` maps to `GET /translation-schema/v1/schemas/site` and lists all schemas associated with the current site. It supports the documented `appId`, `entityType`, `scope`, `paging.limit`, and `paging.cursor` query parameters.
- `get-by-key` maps to `GET /translation-schema/v1/schemas/app-id/{key.appId}/entity-type/{key.entityType}/scope/{key.scope}`.
- Writes are dry-run first and support `--plan-out`, `--plan-in`, `--apply`, `--yes`, and `--receipt-out`.
- `delete` requires `--ack-irreversible` for live apply.
- Updating a schema with an empty field object removes that field. Official Wix docs say the corresponding content field becomes unavailable, so those updates require `--ack-irreversible`.

## Multilingual translation contents

Commands:

- `wix-safe-agent-cli multilingual-translation-contents create --content-json '{"schemaId":"<schema-id>","entityId":"post-1","locale":"fr-FR","fields":{"title":{"value":"Bonjour"}}}'`
- `wix-safe-agent-cli multilingual-translation-contents get --content-id <content-id>`
- `wix-safe-agent-cli multilingual-translation-contents update --content-json '{"id":"<content-id>","schemaId":"<schema-id>","fields":{"title":{"value":"Salut"}}}'`
- `wix-safe-agent-cli multilingual-translation-contents delete --content-id <content-id>`
- `wix-safe-agent-cli multilingual-translation-contents query --filter-json '{"schemaId":{"$eq":"<schema-id>"}}' --limit 100`
- `wix-safe-agent-cli multilingual-translation-contents search --search-json '{"search":{"expression":"bonjour"}}' --limit 100`
- `wix-safe-agent-cli multilingual-translation-contents bulk-create --contents-json '[{"schemaId":"<schema-id>","entityId":"post-1","locale":"fr-FR","fields":{"title":{"value":"Bonjour"}}}]'`
- `wix-safe-agent-cli multilingual-translation-contents bulk-delete --content-ids-json '["<content-id>"]'`
- `wix-safe-agent-cli multilingual-translation-contents bulk-update --contents-json '[{"content":{"id":"<content-id>","schemaId":"<schema-id>","fields":{"title":{"value":"Salut"}}}}]'`
- `wix-safe-agent-cli multilingual-translation-contents update-by-key --content-json '{"schemaId":"<schema-id>","entityId":"post-1","locale":"fr-FR","fields":{"title":{"value":"Salut"}}}'`
- `wix-safe-agent-cli multilingual-translation-contents bulk-update-by-key --contents-json '[{"content":{"schemaId":"<schema-id>","entityId":"post-1","locale":"fr-FR","fields":{"title":{"value":"Salut"}}}}]'`

Notes for Multilingual translation contents:

- The Wix Multilingual app must be installed on the site, and each content item must match an existing translation schema.
- `create` maps to `POST /translation-content/v1/contents`.
- `get` maps to `GET /translation-content/v1/contents/{contentId}`.
- `update` maps to `PATCH /translation-content/v1/contents/{content.id}` and requires `content.id` plus `content.schemaId`.
- `delete` maps to `DELETE /translation-content/v1/contents/{contentId}`.
- `query` maps to `POST /translation-content/v1/contents/query`; `--limit` is capped at 100.
- `search` maps to `POST /translation-content/v1/contents/search`; it can search site translation content regardless of the app that created it.
- Bulk create, delete, update, and update-by-key commands use the official bulk routes and accept up to 100 items.
- `update-by-key` uses `PATCH /translation-content/v1/contents/by-key` and requires `schemaId`, `entityId`, and `locale`.
- Writes are dry-run first and support `--plan-out`, `--plan-in`, `--apply`, `--yes`, and `--receipt-out`.
- `delete` and `bulk-delete` require `--ack-irreversible` for live apply.
- Updating content with an empty field object removes that field, so those updates require `--ack-irreversible`.
- Content Created, Content Deleted, and Content Updated are callback-only events, not CLI commands.

## Multilingual translation published contents

Commands:

- `wix-safe-agent-cli multilingual-translation-published-contents query --filter-json '{"schemaKey.appId":{"$eq":"<app-id>"},"schemaKey.entityType":{"$eq":"post"},"schemaKey.scope":{"$eq":"SITE"}}' --limit 100`

Notes for Multilingual translation published contents:

- This API only queries translated content that Wix has marked as ready to publish.
- `query` maps to `POST /translation-published-content/v3/published-contents/query`.
- The official docs require filters for `schemaKey.appId`, `schemaKey.entityType`, and `schemaKey.scope`; the CLI validates that those filters are present.
- The method returns up to 100 published content items per request and defaults to `id ASC`.
- Published Content Created, Published Content Deleted, and Published Content Updated are callback-only events, not CLI commands.

## Multilingual machine translation

Commands:

- `wix-safe-agent-cli multilingual-machine-translation translate --source-language EN --target-language IT --content-json '{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}'`
- `wix-safe-agent-cli multilingual-machine-translation bulk-translate --source-language EN --target-language IT --contents-json '[{"id":"content-1","format":"PLAIN_TEXT","plainTextContent":"Hello"}]'`

Notes for Multilingual machine translation:

- The Wix Multilingual app must be installed on the site.
- Successful translation requests consume site word credits. Live apply requires `--plan-in`, `--apply`, `--yes`, and `--ack-irreversible`.
- `translate` maps to `POST /machine-translation/v3/machine-translate` and translates one `contentToTranslate` object.
- `bulk-translate` maps to `POST /machine-translation/v3/bulk-machine-translate` and translates up to 1,000 content units.
- The source and target language must be different supported language codes.
- Wix does not overwrite the original content. Store the returned translated content separately if you need it later.
- Only text content is translated. Collapsible text is not supported.
- Each translatable content unit must stay within the official 5,000-character limit; for rich content, the limit applies per node.

## Multilingual machine translation credit data

Commands:

- `wix-safe-agent-cli multilingual-machine-translation-credit-data get`
- `wix-safe-agent-cli multilingual-machine-translation-credit-data check-sufficient --word-count 100`

Notes for Multilingual machine translation credit data:

- The Wix Multilingual app must be installed on the site.
- `get` maps to `GET /translation-credits/v1/credit` and returns the site's word credit data.
- `check-sufficient` maps to `POST /translation-credits/v1/credit/is-eligible` with `wordCount` in the JSON body.
- These commands do not spend credits. Use `check-sufficient` before `multilingual-machine-translation translate` or `bulk-translate` to avoid failed credit-spending translation requests.
- The current official docs have a generated curl mismatch for `check-sufficient`; the rendered REST page and embedded schema say `POST`, so this CLI uses `POST` with a JSON body.

## Online Programs programs

Commands:

- `wix-safe-agent-cli online-programs-programs create --program-json '{"description":{"title":"Course"}}'`
- `wix-safe-agent-cli online-programs-programs get --program-id <program-id>`
- `wix-safe-agent-cli online-programs-programs update --program-json '{"id":"<program-id>","revision":"3","description":{"title":"Updated"}}'`
- `wix-safe-agent-cli online-programs-programs delete --program-id <program-id>`
- `wix-safe-agent-cli online-programs-programs query --query-json '{"filter":{"status":"PUBLISHED"},"paging":{"limit":50}}'`
- `wix-safe-agent-cli online-programs-programs search --search-json '{"search":{"expression":"yoga"},"paging":{"limit":20}}'`
- `wix-safe-agent-cli online-programs-programs count --filter-json '{"status":"PUBLISHED"}'`
- `wix-safe-agent-cli online-programs-programs bulk-update --programs-json '[{"program":{"id":"<program-id>","revision":"3","description":{"title":"Updated"}}}]'`
- `wix-safe-agent-cli online-programs-programs archive --program-id <program-id>`
- `wix-safe-agent-cli online-programs-programs duplicate --program-id <program-id>`
- `wix-safe-agent-cli online-programs-programs end --program-id <program-id>`
- `wix-safe-agent-cli online-programs-programs list-samples`
- `wix-safe-agent-cli online-programs-programs publish --program-id <program-id>`

Notes for Online Programs programs:

- The Wix Online Programs app must be installed on the site.
- Reads/helpers are `get`, `query`, `search`, `count`, and `list-samples`.
- Writes are reviewed-plan commands. Generate a plan first, then apply with `--plan-in`, `--apply`, and `--yes`.
- `update` maps to `PATCH /online-programs/v3/programs/{program.id}` and requires `program.id` plus the current `program.revision`.
- `bulk-update` maps to `POST /online-programs/v3/bulk/programs/update`, accepts up to 100 items, and each item must include `program.id` and `program.revision`.
- `delete` permanently removes a program, cancels its scheduled end task, removes related member groups, and removes it from search; live apply requires `--ack-irreversible`.
- `archive` closes the program, removes it from normal public discovery, and replaces its SEO slug with the program ID; live apply requires `--ack-irreversible`.
- `end` changes a published program to `ENDED` and cancels any scheduled end task; live apply requires `--ack-irreversible`.
- `duplicate` creates a new draft program and `publish` publishes a draft program; both stay plan-first but do not require `--ack-irreversible`.

## Online Programs Instructor V2

Commands:

- `wix-safe-agent-cli online-programs-instructor-v2 create --instructor-json '{"name":"Teacher"}'`
- `wix-safe-agent-cli online-programs-instructor-v2 update --instructor-json '{"id":"<instructor-id>","name":"Teacher"}'`
- `wix-safe-agent-cli online-programs-instructor-v2 query --query-json '{"filter":{"programIds":{"$hasSome":["<program-id>"]}}}'`
- `wix-safe-agent-cli online-programs-instructor-v2 assign --instructor-id <instructor-id> --program-id <program-id>`
- `wix-safe-agent-cli online-programs-instructor-v2 change-program-instructors --assignment-json '{"programId":"<program-id>","assignInstructorIds":["<instructor-id>"]}'`
- `wix-safe-agent-cli online-programs-instructor-v2 invite --email teacher@example.com`
- `wix-safe-agent-cli online-programs-instructor-v2 list --list-json '{"paging":{"limit":50,"offset":0}}'`
- `wix-safe-agent-cli online-programs-instructor-v2 unassign --instructor-id <instructor-id> --program-id <program-id>`

Notes for Online Programs Instructor V2:

- The Wix Online Programs app must be installed on the site.
- `query` and `list` are read/helper commands, even though the official REST methods use `POST`.
- Writes are reviewed-plan commands. Generate a plan first, then apply with `--plan-in`, `--apply`, and `--yes`.
- `create` maps to `POST /_api/instructors-service/v2/instructors` and requires `instructor.name`.
- `update` maps to `PATCH /_api/instructors-service/v2/instructors/{instructor.id}` and requires `instructor.id`.
- `assign` maps to `POST /_api/instructors-service/v2/instructors/{instructorId}/assign` with required `programId`.
- `change-program-instructors` maps to `POST /_api/instructors-service/v2/assignments`, requires `programId`, and accepts up to 10 `assignInstructorIds` plus up to 10 `unassignInstructorIds`.
- `invite` sends an instructor invitation email, so live apply requires `--ack-irreversible`.
- `unassign` removes an instructor assignment from a program, so live apply requires `--ack-irreversible`.
- The official docs use `/_api/instructors-service/v2` paths for this family; this CLI follows those exact official paths.

## B2B site transfer

Commands:

- `wix-safe-agent-cli b2b-site-transfer transfer --site-transfer-json '{"siteId":"<site-id>","sourceAccountId":"<source-account-id>","enableNotifications":false}'`

Notes for B2B site transfer:

- This is an account-level API-key command for Wix strategic partners.
- The target account is sent in the `wix-account-id` header from the configured account ID. The API key is sent in `Authorization`.
- `transfer` maps to `POST /b2b-site-management/v1/transfer-site` and requires `siteTransfer.siteId` plus `siteTransfer.sourceAccountId`.
- Writes are reviewed-plan commands. Generate a plan first, then apply with `--plan-in`, `--apply`, `--yes`, and `--ack-irreversible`.
- Wix docs say sites with paid Wix services cannot be transferred and transfers to unrelated accounts are not possible.
- The official method header and curl use `/b2b-site-management/v1/transfer-site`; one embedded server object mentions `/b2b-site-management/resellers/v1/transferSite`, so this CLI follows the method header and curl.

## Partner Profiles

Commands:

- `wix-safe-agent-cli partner-profiles create --profile-json '{"professionalInformation":{"businessName":"Agency"}}'`
- `wix-safe-agent-cli partner-profiles update --profile-json '{"id":"<partner-id>","revision":"<revision>","professionalInformation":{"businessName":"Agency"}}'`
- `wix-safe-agent-cli partner-profiles delete`
- `wix-safe-agent-cli partner-profiles get-current`
- `wix-safe-agent-cli partner-profiles get-public --partner-id <partner-id>`
- `wix-safe-agent-cli partner-profiles find-public-by-slug --slug <slug>`

Notes for Partner Profiles:

- Official Wix docs mark Partner Profile V1 as Developer Preview.
- Owner-facing commands use account-level API-key auth and require `Manage CRM and Marketplace`.
- Public reads use no auth: `get-public` maps to `GET /partners/profile/v1/partner-profiles/{partnerId}/public`, and `find-public-by-slug` maps to `GET /partners/profile/v1/partner-profiles/slug/{slug}/public`.
- Writes are reviewed-plan commands. Generate a plan first, then apply with `--plan-in`, `--apply`, and `--yes`.
- `update` maps to `PATCH /partners/profile/v1/partner-profiles` and requires `partnerProfile.revision`.
- `delete` removes the current authenticated partner profile and live apply requires `--ack-irreversible`.
- Created and updated profiles enter Wix verification before changes appear in the public profile.
- The official `Contact Partner` method is reserved for Wix first-party client UI and is not exposed as a CLI command.

## Viewer

Commands:

- `wix-safe-agent-cli viewer-cache invalidate --invalidation-methods-json '[{"tag":"products"}]'`
- `wix-safe-agent-cli viewer-seo-tags resolve-item --page-url https://example.com/p/shoe --slug shoe --item-type wix-stores-product`
- `wix-safe-agent-cli viewer-seo-tags resolve-static --page-url https://example.com/about --page-name about`

Notes for Viewer:

- `viewer-cache invalidate` maps to `POST /ssr/v1/invalidate-cache` and is a reviewed-plan write.
- Cache invalidation accepts up to 100 invalidation method objects, each with a non-empty `tag` up to 500 characters.
- Official docs say the Cache API is only supported for developing sites and works only with Web Methods or Router APIs. It does not invalidate the site's SSR cache.
- `viewer-seo-tags resolve-item` maps to `GET /promote/seo/v1/resolve-item-seo-tags`.
- `viewer-seo-tags resolve-static` maps to `GET /promote/seo/v1/resolve-static-page-seo-tags`.
- SEO tag commands require `View SEO Settings` and are read-only helpers.

## GraphQL boundary

There is no `wix-safe-agent-cli graphql` command.

Official Wix docs describe the GraphQL API as a unified schema where callers send arbitrary query or mutation details to a GraphQL endpoint. That would be a generic GraphQL bridge in this safe CLI. Use the explicit named REST-backed command families instead.

## Generic async job runner boundary

There is no generic async job runner command.

Official Wix Async Job docs expose explicit read methods, already shipped as `async-jobs get` and `async-jobs list-items`. A command that starts, dispatches, or generically runs arbitrary async jobs would not map to an official named Wix method, so this safe CLI does not expose one.

## Send notifications (plan-first write)

- `wix-safe-agent-cli --plan-out plan.json notifications notify --notification-template-id <id> [--dynamic-values-json '{...}']`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json notifications notify --notification-template-id <id> [--dynamic-values-json '{...}'] [--receipt-out receipt.json]`

Notes for Notifications:
- `notifications notify` uses this tool's standard site-context Wix app-token or Wix user-identity auth path.
- `notifications notify` is plan-first: `--plan-out`, then `--plan-in --apply --yes`.
- Required request permission scope is `Manage Notifications` (`SCOPE.DC-NOTIFICATIONS.MANAGE-NOTIFICATIONS`).
- `--notification-template-id` is required and must be a valid template id.
- `--dynamic-values-json` is a JSON map from placeholder string to object, and each object must include a `text` string.
- The command precondition includes `up to 100,000 calls per month for each site`.
- Verification is provider-response only: success is based on receiving `notificationBatchId`; this boundary does not claim delivery proof.
- This boundary does not claim full delivery verification yet and is live-unverified until delivery proof is available in this scope.

## Read site URLs

- `wix-safe-agent-cli site-urls get-editor-urls`
- `wix-safe-agent-cli site-urls list-published-site-urls`

Notes for Site URLs:
- Both methods are read-only family members.
- `site-urls get-editor-urls` is read-only in this wrapper path.
- `site-urls list-published-site-urls` can return empty arrays for unpublished sites.
- This boundary is locally unit-tested and live-unverified.

## Create projects (account-level)

- `wix-safe-agent-cli projects create-project --name <name> --type WIX [--template-id <template_id>] [--folder-id <folder_id>] [--apps-json '<app_payload>']`

Notes:
- `projects create-project` uses the same account-level auth path as `sites`: `WIX_API_KEY` + `WIX_ACCOUNT_ID`.
- This boundary posts to `POST /funnel/projects/v1/create` and always requires `--name` locally.
- This boundary accepts only `--type WIX`.
- This boundary supports optional request fields: `--template-id`, `--folder-id`, and `--apps-json`.
- `--name` is required by this boundary even though the provider method schema marks it optional.
- The command is dry-run first and requires `--plan-in --apply --yes` for live applies.
- The command does not require `--ack-irreversible`.
- It supports `--plan-out`, `--plan-in`, and `--receipt-out`.
- Official account-level Projects docs currently expose only `create-project`; there is no documented `projects get/list/query` method family in this subtree.
- Success is verified from the create response only by checking `project.metaSiteId` and `project.siteId`.
- If `--template-id` or `--apps-json` are sent, the tool also checks the returned project fields match the requested values.
- For existing sites, use account-level Sites commands (`sites query`, `sites count`) as documented.

## Account-level Sites Skills recipes

There is no `sites-skills` command. Official Wix Account Level Sites Skills docs are recipes, not a separate REST family.

Notes:
- The official `Query Sites` recipe uses `POST /site-list/v2/sites/query`, which is already exposed as `wix-safe-agent-cli sites query`.
- The official `Create Site from Template` recipe combines template search, site/project creation, optional publishing, and optional Headless OAuth App creation. Use the explicit shipped commands for the stable pieces that are in this tool boundary: `sites query`, `projects create-project`, `site-actions publish`, and `headless-oauth-apps create`.
- The recipe's template-search endpoint is not a separate documented Account Level Sites REST method family in the API reference, so this CLI does not expose a generic template-search bridge under `sites-skills`.

## Account-level Resellers

Commands:

- `wix-safe-agent-cli resellers get --package-id <id>`
- `wix-safe-agent-cli resellers query --filter-json '{"externalId":{"$eq":"..."}}' --limit 100`
- `wix-safe-agent-cli resellers create-package --body-json @package.json`
- `wix-safe-agent-cli resellers adjust-product-instance --instance-id <id> --body-json '{"catalogProductId":"..."}'`
- `wix-safe-agent-cli resellers assign-product-instance --instance-id <id> --site-id <site-id>`
- `wix-safe-agent-cli resellers unassign-product-instance --instance-id <id>`
- `wix-safe-agent-cli resellers update-package-external-id --package-id <id> --external-id <external-id>`
- `wix-safe-agent-cli resellers cancel-package --package-id <id>`
- `wix-safe-agent-cli resellers cancel-product-instance --instance-id <id>`

Notes:
- Resellers uses account-level API-key auth: set `WIX_API_KEY` and `WIX_ACCOUNT_ID`.
- `get` maps to `GET /resellers/v1/packages/{id}`.
- `query` maps to `POST /resellers/v1/packages/query`; `--limit` is capped at 100.
- `create-package` maps to `POST /resellers/v2/packages`.
- `adjust-product-instance` maps to `PATCH /resellers/v1/packages/product-instances/{instanceId}` and requires a body with `catalogProductId` or `billingInfo`.
- `assign-product-instance` maps to `PATCH /resellers/v1/packages/product-instances/{instanceId}/{siteId}`.
- `unassign-product-instance` maps to `PATCH /resellers/v1/packages/product-instances/{instanceId}/unassign`.
- `update-package-external-id` maps to `PATCH /resellers/v1/packages/update/{packageId}/{externalId}` and limits `--external-id` to 100 characters.
- `cancel-package` maps to `DELETE /resellers/v1/packages/{id}`.
- `cancel-product-instance` maps to `DELETE /resellers/v1/packages/product-instances/{instanceId}`.
- Writes are dry-run first and support `--plan-out`, `--plan-in`, `--apply`, `--yes`, and `--receipt-out`.
- Cancel commands remove customer access and require `--ack-irreversible` for live apply.

## Change site actions (account-level)

- `wix-safe-agent-cli site-actions bulk-delete --site-ids-json '["..."]'`
- `wix-safe-agent-cli site-actions duplicate --source-site-id <id> --site-display-name <name>`
- `wix-safe-agent-cli site-actions publish --site-id <id>`

Notes:
- `site-actions bulk-delete` uses the same account-level auth path as `sites`: `WIX_API_KEY` + `WIX_ACCOUNT_ID`.
- `site-actions bulk-delete` supports up to 20 site IDs per request.
- This action is not a permanent delete. Official Wix docs describe it as move-to-trash behavior.
- `site-actions bulk-delete` is dry-run first and requires `--apply --yes --ack-irreversible` for live apply.
- `site-actions bulk-delete` preflights all requested site IDs through `sites query`, refuses missing IDs, rejects stale `--plan-in` apply drift, and verifies success from the provider response using per-item metadata plus `bulkActionMetadata`.
- `site-actions duplicate` uses the same account-level auth path as `sites`: `WIX_API_KEY` + `WIX_ACCOUNT_ID`.
- `site-actions duplicate` is dry-run first and requires `--apply --yes` for live apply.
- `site-actions duplicate` does not require `--ack-irreversible`.
- `site-actions duplicate` supports `--plan-out`, `--plan-in`, and `--receipt-out`.
- `site-actions duplicate` preflights `--source-site-id` with `sites query`, refuses missing source sites, rejects stale `--plan-in` apply drift, and requires `newSiteId` from the provider response.
- `site-actions duplicate` verifies the duplicated site exists by querying the `newSiteId` returned by the provider.
- `site-actions duplicate` is intentionally incomplete for some data areas (`orders`, `contacts`, `invoices`, some 3rd-party app settings, domain, and Premium capabilities).
- `site-actions duplicate` maps to official route `POST /site-actions/v1/sites/duplicate`.
- Official Site Actions docs are currently inconsistent, and publish uses `wix-site-id` header semantics in API-key mode.
- `site-actions publish` uses official route `POST /site-publisher/v1/site/publish`.
- `site-actions publish` success response is `{}` and is treated as successful only after verification.
- `site-actions publish` is dry-run first and requires `--apply --yes` for live apply.
- `site-actions publish` does not require `--ack-irreversible`.
- `site-actions publish` supports `--plan-out`, `--plan-in`, and `--receipt-out`.
- `site-actions publish` preflights the `--site-id` through `sites query`, refuses missing IDs, and rejects stale `--plan-in` apply drift.
- `site-actions publish` verifies success by re-querying the site and checking `published=true`.
- `site-actions publish` receipts may show `changed: false` when the site was already published before apply; this is expected.

## Manage site folders (account-level)

- `wix-safe-agent-cli site-folders query [--query-json '{...}'] [--filter-json '{...}'] [--sort-json '[{...}]'] [--limit N] [--offset N]`
- `wix-safe-agent-cli site-folders get-folder-by-site --site-id <id>`
- `wix-safe-agent-cli site-folders create --name <folder_name> [--parent-id <folder_id>]`
- `wix-safe-agent-cli site-folders update --folder-id <id> --name <new_name>`
- `wix-safe-agent-cli site-folders delete --folder-id <id>`
- `wix-safe-agent-cli site-folders move-folders --folder-ids-json '["..."]' [--target-folder-id <id> | --to-root]`
- `wix-safe-agent-cli site-folders move-sites --site-ids-json '["..."]' [--target-folder-id <id> | --to-root]`

Notes:
- Site Folders uses the same account-level auth path as `sites`: `WIX_API_KEY` + `WIX_ACCOUNT_ID`.
- Official Wix docs mark Site Folders as API-key-only and available to selected beta users.
- `site-folders query` defaults to `--limit 1000` and refuses `--limit` above `1000`.
- `site-folders query` supports folder filters only for `name`, `id`, and `parentId`.
- `site-folders get-folder-by-site` can return an empty folder object when the site is at root level.
- `site-folders update` is a rename-only command and sends `fieldMask: "name"`.
- `site-folders delete` requires `--apply --yes --ack-irreversible`, captures a before-state snapshot, refuses stale `--plan-in` apply drift, and verifies removal by querying the folder ID afterward.
- `site-folders move-folders` supports up to 1000 folder IDs, snapshots current folder state during plan/apply preflight, refuses missing folders and stale `--plan-in` apply drift, and verifies final parent assignments after apply.
- `site-folders move-sites` supports up to 500 site IDs, snapshots current folder assignments during plan/apply preflight, refuses stale `--plan-in` apply drift, and verifies final assignments with per-site `get-folder-by-site` checks.

## Read and manage files

- `wix-safe-agent-cli files list [--parent-folder-id <id>] [--media-types-json '["..."]'] [--private true|false] [--sort-json '{...}']`
- `wix-safe-agent-cli files get --file-id <id-or-url>`
- `wix-safe-agent-cli files batch-get --file-ids-json '["..."]'`
- `wix-safe-agent-cli files search [--search <text>] [--media-types-json '["..."]'] [--private true|false] [--root-folder <value>] [--sort-json '{...}'] [--cursor <cursor>] [--limit N]`
- `wix-safe-agent-cli files query [--query-json '{...}']`
- `wix-safe-agent-cli files list-deleted [--parent-folder-id <id>] [--media-types-json '["..."]'] [--private true|false] [--sort-json '{...}'] [--cursor <cursor>]`
- `wix-safe-agent-cli files update --file-id <id-or-url> --file-json '{...}'`
- `wix-safe-agent-cli files bulk-delete --file-ids-json '["..."]' [--permanent true|false]`
- `wix-safe-agent-cli files bulk-restore --file-ids-json '["..."]'`
- `wix-safe-agent-cli files generate-upload-url --upload-json '{...}'`
- `wix-safe-agent-cli files generate-resumable-upload-url --upload-json '{...}'`
- `wix-safe-agent-cli files import --import-json '{...}'`
- `wix-safe-agent-cli files generate-download-url --download-json '{...}'`

Notes:

- `files` uses the same Wix app or Wix user identity auth path as `media-folders`.
- `files list` and `files list-deleted` stay on the official `100` item page limit in this tool.
- `files batch-get` stays on the official `100` file read limit in this tool.
- `files bulk-delete` and `files bulk-restore` support up to `1000` file IDs or Wix media URLs per call, matching the official method pages.
- `files update`, `files bulk-delete`, `files bulk-restore`, and `files import` are dry-run first and require a reviewed saved plan for live apply: `--plan-out`, then `--plan-in --apply --yes`.
- `files bulk-delete` also requires `--ack-irreversible` for live apply because permanent delete is irreversible and even non-permanent delete removes files from the active tree.
- `files update` captures the current file descriptor before planning and refuses stale reviewed plans if the file changed before apply.
- `files bulk-delete` captures current file descriptors before planning only when the request stays within the shipped `100`-file batch-get snapshot limit. Larger delete plans keep the no-snapshot recovery limit explicit instead of pretending stronger rollback exists.
- `files bulk-restore` keeps recovery limits explicit because this tool does not ship a direct deleted-file get-by-id read path for trash-bin state.
- `files import` is plan-first because it creates new Media Manager state from an external URL and has no useful target before-state snapshot.
- `files generate-upload-url`, `files generate-resumable-upload-url`, and `files generate-download-url` are non-mutating POST helpers. They return official Wix helper URLs, but the actual upload or download then happens outside this CLI.

## Manage media folders

- `wix-safe-agent-cli media-folders list [--parent-folder-id <id>] [--cursor <cursor>] [--limit N] [--sort-json '{...}']`
- `wix-safe-agent-cli media-folders get --folder-id <id>`
- `wix-safe-agent-cli media-folders search [--search <text>] [--root-folder MEDIA_ROOT|TRASH_ROOT|VISITOR_UPLOADS_ROOT] [--cursor <cursor>] [--limit N] [--sort-json '{...}']`
- `wix-safe-agent-cli media-folders query [--query-json '{...}'] [--sort-json '[{...}]'] [--limit N] [--offset N]`
- `wix-safe-agent-cli media-folders list-deleted [--parent-folder-id <id>] [--cursor <cursor>] [--limit N] [--sort-json '{...}']`
- `wix-safe-agent-cli media-folders create --display-name <name> [--parent-folder-id <id>]`
- `wix-safe-agent-cli media-folders update --folder-id <id> [--display-name <name>] [--parent-folder-id <id>]`
- `wix-safe-agent-cli media-folders bulk-delete --folder-ids-json '["..."]' [--permanent true|false]`
- `wix-safe-agent-cli media-folders bulk-restore --folder-ids-json '["..."]'`
- `wix-safe-agent-cli media-folders generate-download-url --folder-id <id>`

Notes:

- `media-folders` uses the same Wix app or Wix user identity auth path as the Media Manager files commands.
- `media-folders list` and `media-folders list-deleted` follow the official `100` item page limit in this tool.
- `media-folders search` and `media-folders query` follow the official `200` item result limit in this tool.
- `media-folders create`, `media-folders update`, `media-folders bulk-delete`, and `media-folders bulk-restore` are dry-run first and require a reviewed saved plan for live apply: `--plan-out`, then `--plan-in --apply --yes`.
- `media-folders bulk-delete` also requires `--ack-irreversible` for live apply because permanent delete is irreversible and non-permanent delete still removes folders from the active tree.
- `media-folders update` captures the current folder before planning and refuses stale reviewed plans if the folder changed before apply.
- `media-folders bulk-delete` captures current active folder state before planning and refuses stale reviewed plans if any targeted folder changed before apply.
- `media-folders bulk-restore` keeps recovery limits explicit: Wix documents restore from trash, but this family does not expose a direct trash-bin get-by-id read for a stronger before-state snapshot in this tool.
- `media-folders generate-download-url` is a non-mutating POST helper that returns a download URL for one folder archive.

## Wix Skills / Media skills

There is no `media-skills` command. Official Wix Skills docs describe installable `SKILL.md` instruction files for AI tools, not callable Wix REST or SDK operations. The callable Media Manager API surface is covered by the `files` and `media-folders` command families above.

## HTTP Functions

There is no generic `http-functions call` command. Official Wix HTTP Functions docs define a site-defined invoker for custom Velo functions at `/{functionName}`. Because the function name and behavior are created by the site owner, exposing that endpoint here would be a call-anything bridge, not an explicit named Wix API command. Site-specific projects can build approved wrappers for known functions outside this generic Wix safe CLI.

## Convert and validate Rich Content Ricos documents

- `wix-safe-agent-cli rich-content-ricos convert-from --convert-json @convert.json`
- `wix-safe-agent-cli rich-content-ricos convert-to --convert-json @convert.json`
- `wix-safe-agent-cli rich-content-ricos validate --validate-json @validate.json`

Notes for Rich Content Ricos:
- These commands call official Ricos Documents helper methods. They convert or validate caller-supplied content and do not create persistent Wix state.
- `convert-from` converts a Ricos document to another format, such as Markdown, HTML, or plain text.
- `convert-to` converts content such as Markdown, HTML, or plain text to a Ricos document.
- `validate` checks whether a Ricos document is valid for the supplied plugins and can ask Wix to return a fixed document.
- Official docs say these methods require `Manage Ricos Document`.
- This family remains live-unverified.

## Read and manage Pro Gallery galleries

- `wix-safe-agent-cli pro-gallery list-galleries [--params-json '{"limit":10}']`
- `wix-safe-agent-cli pro-gallery get-gallery --gallery-id <gallery_id>`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery create-gallery --gallery-json @gallery.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pro-gallery create-gallery --gallery-json @gallery.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery update-gallery --gallery-id <gallery_id> --gallery-json @gallery.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pro-gallery update-gallery --gallery-id <gallery_id> --gallery-json @gallery.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery delete-gallery --gallery-id <gallery_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json pro-gallery delete-gallery --gallery-id <gallery_id> [--receipt-out receipt.json]`

## Read and manage Pro Gallery items

- `wix-safe-agent-cli pro-gallery list-gallery-items --gallery-id <gallery_id> [--params-json '{"limit":10}']`
- `wix-safe-agent-cli pro-gallery get-gallery-item --gallery-id <gallery_id> --item-id <item_id>`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery create-gallery-item --gallery-id <gallery_id> --item-json @item.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pro-gallery create-gallery-item --gallery-id <gallery_id> --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery update-gallery-item --gallery-id <gallery_id> --item-id <item_id> --item-json @item.json`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json pro-gallery update-gallery-item --gallery-id <gallery_id> --item-id <item_id> --item-json @item.json [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery delete-gallery-item --gallery-id <gallery_id> --item-id <item_id>`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json pro-gallery delete-gallery-item --gallery-id <gallery_id> --item-id <item_id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --plan-out plan.json pro-gallery bulk-delete-gallery-items --gallery-id <gallery_id> --delete-json @delete.json`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json pro-gallery bulk-delete-gallery-items --gallery-id <gallery_id> --delete-json @delete.json [--receipt-out receipt.json]`

Notes for Pro Gallery:
- Official docs say API-created galleries are backend-only until connected manually to a widget in the Wix Editor.
- Official docs say gallery media items must already exist in Media Manager.
- Official generated docs currently show both `pro-gallery` and `progallery` path spellings; this CLI uses the rendered Method API Endpoint and curl spelling under `/progallery/v2/...`.
- Delete commands are reviewed-plan writes and require `--ack-irreversible`.
- The deprecated Delete Gallery Items method is not exposed; use `bulk-delete-gallery-items`.
- This family remains live-unverified.

## Read data items

- `wix-safe-agent-cli data-items get --data-item-id <id> --data-collection-id <id> [--consistent-read] [--language <bcp47>] [--fields-json '["..."]'] [--include-references-json '{...}']`
- `wix-safe-agent-cli data-items query --data-collection-id <id> [--query-json '{...}'] [--filter-json '{...}'] [--sort-json '{...}'] [--fields-json '["..."]'] [--include-references-json '{...}'] [--include-field-groups-json '["..."]'] [--language <bcp47>] [--limit N] [--offset N] [--cursor <cursor>] [--return-total-count] [--consistent-read]`
- `wix-safe-agent-cli data-items aggregate --data-collection-id <id> --aggregation-json '{...}' [--initial-filter-json '{...}'] [--final-filter-json '{...}'] [--sort-json '{...}'] [--limit N] [--offset N] [--cursor <cursor>] [--app-options-json '{...}'] [--language <bcp47>] [--return-total-count] [--consistent-read] [--include-draft-items]`
- `wix-safe-agent-cli data-items aggregate-pipeline --data-collection-id <id> --pipeline-json '{...}' [--app-options-json '{...}'] [--language <bcp47>] [--return-total-count] [--consistent-read] [--include-draft-items]`
- `wix-safe-agent-cli data-items distinct --data-collection-id <id> --field-name <field> [--filter-json '{...}'] [--order ASC|DESC] [--limit N] [--offset N] [--cursor <cursor>] [--language <bcp47>] [--return-total-count] [--consistent-read] [--include-draft-items]`
- `wix-safe-agent-cli data-items query-referenced --data-collection-id <id> --referring-item-field-name <field> --referring-item-id <id> [--fields-json '["..."]'] [--language <bcp47>] [--order ASC|DESC] [--limit N] [--offset N] [--cursor <cursor>] [--return-total-count] [--consistent-read] [--include-draft-items] [--include-hidden-products] [--include-variants]`
- `wix-safe-agent-cli data-items count --data-collection-id <id> [--query-json '{...}'] [--filter-json '{...}'] [--language <bcp47>] [--consistent-read]`
- `wix-safe-agent-cli data-items search --data-collection-id <id> --search-json '{...}' [--include-references-json '{...}'] [--referenced-item-options-json '{...}'] [--include-draft-items]`
- `wix-safe-agent-cli data-items is-referenced --data-collection-id <id> --referring-item-field-name <field> --referring-item-id <id> --referenced-item-id <id> [--consistent-read]`

Notes:

- `data-items aggregate` uses a required aggregation object plus optional `initialFilter` and `finalFilter` request bodies. It supports either offset paging or cursor paging, but not both in one call.
- `data-items aggregate-pipeline` sends the full pipeline object in `--pipeline-json`. This command does not expose separate top-level paging flags because paging belongs inside the pipeline payload for this method.
- `data-items distinct` reads distinct values from one field and supports either offset paging or cursor paging, but not both in one call.
- `data-items search` sends the full Wix search body through `--search-json`. Use `--include-references-json` and `--referenced-item-options-json` only for the documented top-level related-item options.

## Change data-item relationships

- `wix-safe-agent-cli data-items insert-reference --data-collection-id <id> --referring-item-field-name <field> --referring-item-id <id> --referenced-item-id <id> [--consistent-read]`
- `wix-safe-agent-cli data-items remove-reference --data-collection-id <id> --referring-item-field-name <field> --referring-item-id <id> --referenced-item-id <id> [--consistent-read]`
- `wix-safe-agent-cli data-items replace-references --data-collection-id <id> --referring-item-field-name <field> --referring-item-id <id> --new-referenced-item-ids-json '[...]' [--consistent-read]`

Notes:

- `replace-references` accepts an empty `[...]` to clear all references on that field.
- These relationship commands are dedicated reference-mutation APIs and are separate from normal item insert/update/patch/remove flows.

## Collection schema

- `wix-safe-agent-cli data-collections list [--fields-json '["..."]'] [--limit N] [--offset N] [--sort-field-name <field>] [--sort-order ASC|DESC] [--consistent-read]`
- `wix-safe-agent-cli data-collections get --data-collection-id <id> [--fields-json '["..."]'] [--consistent-read]`
- `wix-safe-agent-cli data-collections create --collection-id <id> [--display-name <name>] [--display-field <field>] --field-json '<field_json>' [--field-json '<field_json>'] [--permission-insert ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-update ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-remove ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-read ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE]`
- `wix-safe-agent-cli data-collections update --data-collection-id <id> [--display-name <name>] [--display-field <field>] [--field-json '<field_json>' ...] [--permission-insert ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-update ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-remove ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-read ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE]`
- `wix-safe-agent-cli data-collections patch --data-collection-id <id> [--display-name <name>] [--display-field <field>] [--permission-insert ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-update ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-remove ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE] [--permission-read ADMIN|SITE_MEMBER_AUTHOR|SITE_MEMBER|ANYONE]`
- `wix-safe-agent-cli data-collections delete --data-collection-id <id>`

## Change collection fields and plugins

- `wix-safe-agent-cli data-collections create-field --data-collection-id <id> --field-json '<field_json>'`
- `wix-safe-agent-cli data-collections update-field --data-collection-id <id> --field-json '<field_json>'`
- `wix-safe-agent-cli data-collections patch-field --data-collection-id <id> --field-json '<field_json>'`
- `wix-safe-agent-cli data-collections delete-field --data-collection-id <id> --field-key <field_key> --ack-irreversible`
- `wix-safe-agent-cli data-collections add-plugin --data-collection-id <id> --plugin-json '<plugin_json>'`
- `wix-safe-agent-cli data-collections delete-plugin --data-collection-id <id> --plugin-type <plugin_type>`

Notes:

- All `data-collections` write commands are dry-run by default and apply with `--apply --yes`.
- `data-collections create`, `update`, `patch`, `create-field`, `update-field`, `patch-field`, `add-plugin`, and `delete-plugin` are reviewed-plan writes.
- `data-collections delete` and `data-collections delete-field` still require `--ack-irreversible`.
- `data-collections delete-field` can remove existing values from items across the collection.
- `data-collections add-plugin` and `data-collections delete-plugin` can change collection behavior broadly.
- `data-collections patch` stays narrow to `displayName`, `displayField`, and `permissions`; fields and plugins use the dedicated commands above.
- All `data-collections` writes use Wix app or Wix user identity auth and require `Manage Data Collections`.
- Verification is by collection reread where the method supports it.

## Change data items

- `wix-safe-agent-cli data-items insert --data-collection-id <id> --data-item-json '{...}' [--language <bcp47>]`
- `wix-safe-agent-cli --plan-out plan.json data-items save --data-collection-id <id> --data-item-json '{...}' [--app-options-json '{...}'] [--include-draft-items]`
- `wix-safe-agent-cli --plan-out plan.json data-items truncate --data-collection-id <id>`
- `wix-safe-agent-cli data-items bulk-insert --data-collection-id <id> --data-items-json '[{...}]' [--app-options-json '{...}'] [--return-entity]`
- `wix-safe-agent-cli data-items bulk-patch --data-collection-id <id> --patches-json '[{...}]' [--condition-json '{...}']`
- `wix-safe-agent-cli --plan-out plan.json data-items bulk-remove --data-collection-id <id> --data-item-ids-json '["..."]' [--condition-json '{...}'] [--app-options-json '{...}'] [--include-draft-items]`
- `wix-safe-agent-cli --plan-out plan.json data-items bulk-save --data-collection-id <id> --data-items-json '[{...}]' [--app-options-json '{...}'] [--include-draft-items] [--return-entity]`
- `wix-safe-agent-cli --plan-out plan.json data-items bulk-update --data-collection-id <id> --data-items-json '[{...}]' [--condition-json '{...}'] [--app-options-json '{...}'] [--include-draft-items] [--return-entity]`
- `wix-safe-agent-cli --plan-out plan.json data-items bulk-insert-references --data-collection-id <id> --data-item-references-json '[{...}]' [--return-entity]`
- `wix-safe-agent-cli --plan-out plan.json data-items bulk-remove-references --data-collection-id <id> --data-item-references-json '[{...}]'`
- `wix-safe-agent-cli data-items update --data-collection-id <id> --data-item-id <id> --data-item-json '{...}' [--condition-json '{...}'] [--language <bcp47>]`
- `wix-safe-agent-cli data-items patch --data-collection-id <id> --data-item-id <id> --patch-json '{...}' [--condition-json '{...}'] [--language <bcp47>]`
- `wix-safe-agent-cli data-items remove --data-collection-id <id> --data-item-id <id> [--condition-json '{...}'] [--language <bcp47>]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-items save --data-collection-id <id> --data-item-json '{...}' [--app-options-json '{...}'] [--include-draft-items] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-items truncate --data-collection-id <id> [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --ack-irreversible --plan-in plan.json data-items bulk-remove --data-collection-id <id> --data-item-ids-json '["..."]' [--condition-json '{...}'] [--app-options-json '{...}'] [--include-draft-items] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-items bulk-save --data-collection-id <id> --data-items-json '[{...}]' [--app-options-json '{...}'] [--include-draft-items] [--return-entity] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-items bulk-update --data-collection-id <id> --data-items-json '[{...}]' [--condition-json '{...}'] [--app-options-json '{...}'] [--include-draft-items] [--return-entity] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-items bulk-insert-references --data-collection-id <id> --data-item-references-json '[{...}]' [--return-entity] [--receipt-out receipt.json]`
- `wix-safe-agent-cli --apply --yes --plan-in plan.json data-items bulk-remove-references --data-collection-id <id> --data-item-references-json '[{...}]' [--receipt-out receipt.json]`

Notes:
- All write commands are dry-run by default.
- Apply live writes with `--apply --yes`.
- `data-items remove`, `data-items truncate`, `data-items bulk-remove`, `data-collections delete`, and `data-collections delete-field` still require `--ack-irreversible`.
- Reference write commands (`insert-reference`, `remove-reference`, `replace-references`) do not require `--ack-irreversible`.
- `data-items save`, `truncate`, `bulk-remove`, `bulk-save`, `bulk-update`, `bulk-insert-references`, and `bulk-remove-references` are reviewed-plan writes and require `--plan-out` first, then `--plan-in --apply --yes` for live execution.
- `data-items bulk-insert` supports up to 1,000 items per request.
- `data-items bulk-insert` refuses duplicate explicit IDs in one request and refuses apply if any explicit ID already exists in Wix.
- `data-items bulk-insert` refuses apply when some items do not provide explicit IDs unless `--return-entity` is enabled for safer provider-side verification.
- `data-items bulk-insert` verifies apply using provider bulk metadata and, when explicit IDs are known, read-back GET checks for each inserted item.
- `data-items bulk-patch` supports up to 100 patch objects per request.
- `data-items bulk-patch` refuses duplicate `dataItemId` values in one request and requires non-empty `fieldModifications` for every patch object.
- `data-items bulk-patch` records before-state snapshots for every target item in the plan and refuses stale `--plan-in` apply runs when any item changed after planning.
- `data-items bulk-patch` verifies apply using provider bulk metadata and read-back GET checks for every patched item.
- `data-items save` is an upsert write and verifies by rereading the saved item ID returned by Wix.
- `data-items truncate` verifies by rereading collection count and expecting `0`. No useful item-level rollback snapshot exists.
- `data-items bulk-remove` verifies by rereading each target item and expecting read-back absence / `404`.
- `data-items bulk-save` is an upsert write. If any item has no explicit ID, this tool refuses live apply unless `--return-entity` is enabled so verification can rely on returned IDs.
- `data-items bulk-update` is full-replace behavior and every item must include `id`.
- `data-items bulk-insert-references` refuses no-op apply when all target references already exist and verifies through official `is-referenced` readback.
- `data-items bulk-remove-references` refuses no-op apply when none of the target references exist and verifies through official `is-referenced` readback.
- `data-collections patch` sends `PATCH /wix-data/v2/collections/{dataCollectionId}` and requires exact command form: `PATCH` body root is `dataCollection`.
- `data-collections create` refuses when the collection exists during plan and apply preflight, and applies with read-back GET verification after a live create.
- `data-collections patch` supports only `displayName`, `displayField`, and `permissions`; permission args are merged against current permissions. Field and plugin changes use the dedicated commands above.
- `data-collections update` is a plan-first full-replace flow: it reads the current collection first, preserves current `displayName`, `displayField`, `fields`, `permissions`, and `plugins` when overrides are omitted, carries current `revision`, refuses no-op updates and stale `--plan-in` apply drift, and verifies with read-back GET after apply.
- `data-collections delete` reads the current collection first with consistent read, refuses missing collections, requires `--apply --yes --ack-irreversible`, rejects stale `--plan-in` drift, and verifies deletion by GET returning 404.
- `data-items insert-reference` refuses when the reference already exists.
- `data-items remove-reference` refuses when the reference does not exist.
- `data-items replace-references` refuses no-op updates when requested reference IDs already match the current state.

## Review past runs

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `wix-safe-agent-cli runs list [--limit 20]`
- `wix-safe-agent-cli runs show --run-id 2026-01-19T104512Z_a3f91c`

## Plan and receipt examples

Use the real write families above when you want to see the plan-then-apply workflow.
The current shipped CLI does not include a generic demo command or a generic batch-runner command.
