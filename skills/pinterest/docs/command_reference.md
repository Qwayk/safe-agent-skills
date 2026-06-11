# Command reference

Use this page when you need the exact Pinterest command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Auth

- `pinterest-api-tool auth check`
- `pinterest-api-tool auth login` (currently returns a safety refusal before token exchange or local token writes)
- `pinterest-api-tool auth token set --file token.json` (currently returns a safety refusal before local token writes)
- `pinterest-api-tool auth token status`
- `pinterest-api-tool auth code exchange --code CODE --redirect-uri http://localhost/ --continuous-refresh` (currently returns a safety refusal before token exchange or local token writes)

## Inventory

- `pinterest-api-tool boards list`
- `pinterest-api-tool boards get --id BOARD_ID`
- `pinterest-api-tool boards create --name "Board name"` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool boards update --id BOARD_ID --name "New name"` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool boards delete --id BOARD_ID` (dry-run plan; apply attempt also needs `--ack-irreversible`, then requires explicit no-snapshot approval before write)
- `pinterest-api-tool boards ensure --name "Board name"` (idempotent dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool board-sections list --board-id BOARD_ID`
- `pinterest-api-tool board-sections create --board-id BOARD_ID --name "Section"` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool board-sections update --board-id BOARD_ID --section-id SECTION_ID --name "New section name"` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool board-sections delete --board-id BOARD_ID --section-id SECTION_ID` (dry-run plan; apply attempt also needs `--ack-irreversible`, then requires explicit no-snapshot approval before write)
- `pinterest-api-tool board-sections ensure --board-id BOARD_ID --name "Section"` (idempotent dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool pins list`
- `pinterest-api-tool pins get --id PIN_ID`
- `pinterest-api-tool pins create --board-id BOARD_ID --media-source-type image_url --media-url https://example.com/image.jpg [--link https://example.com/page]` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool pins update --id PIN_ID --title "New title"` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool pins delete --id PIN_ID` (dry-run plan; apply attempt also needs `--ack-irreversible`, then requires explicit no-snapshot approval before write)
- `pinterest-api-tool pins save --id SOURCE_PIN_ID --board-id BOARD_ID [--board-section-id SECTION_ID]` (dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool pins ensure --board-id BOARD_ID --link https://example.com/page --media-source-type image_url --media-url https://example.com/image.jpg` (idempotent dry-run plan; apply attempt requires explicit no-snapshot approval before write)
- `pinterest-api-tool board-pins list --board-id BOARD_ID [--section-id SECTION_ID]`
- `pinterest-api-tool pins links plan --pins-json PATH --out plan.json --canonical-host example.com [--allowed-host HOST]...`
- `pinterest-api-tool pins links apply --plan plan.json` (read-only dry-run preview; apply attempt requires explicit no-snapshot approval before write)

Notes:
- List commands support pagination via `--limit`, `--page-size`, and `--bookmark`.
- Business Access (optional) is supported via `--ad-account-id` on most commands.

Useful inventory flags:
- `pinterest-api-tool boards list --privacy SECRET` (requires appropriate scope)
- `pinterest-api-tool pins list --include-protected-pins` (requires appropriate scope)
- `pinterest-api-tool pins list --creative-types REGULAR,VIDEO`
- `pinterest-api-tool pins list --pin-metrics`
- `pinterest-api-tool board-pins list --board-id BOARD_ID --creative-types REGULAR,VIDEO --pin-metrics`
- `pinterest-api-tool board-pins list --board-id BOARD_ID --section-id SECTION_ID`
  - When `--section-id` is used, Pinterest uses a different endpoint and `--creative-types/--pin-metrics` are not supported.

Pins writes (safety + idempotence notes):
- `pins create|update|delete|save|ensure` are dry-run by default and require `--apply --yes` to attempt apply. Current apply attempts require explicit no-snapshot approval before write.
- `pins delete` additionally requires `--ack-irreversible` before the refusal point.
- `--allow-mismatch` is a sharp tool:
  - for `pins create`/`pins save`, it allows duplicates even when the tool can detect an existing destination match
  - for future live writes, it may bypass strict mismatch refusal
- `pins ensure` is idempotent by **canonicalized `--link` + destination (board/section)**; it refuses when multiple destination pins match.

## User account discovery (read-only)

- `pinterest-api-tool user-account get`
- `pinterest-api-tool user-account businesses`
- `pinterest-api-tool user-account followers`
- `pinterest-api-tool user-account following`
- `pinterest-api-tool user-account following-boards`
- `pinterest-api-tool user-account websites list`
- `pinterest-api-tool user-account websites verification`

Notes:
- List commands support pagination via `--limit`, `--page-size`, and `--bookmark`.
- Use `--param key=value` to pass through supported filters for a specific endpoint.

## Business Access (read-only)

All commands require `--business-id`.

- `pinterest-api-tool business-access --business-id BUSINESS_ID assets list`
- `pinterest-api-tool business-access --business-id BUSINESS_ID members list`
- `pinterest-api-tool business-access --business-id BUSINESS_ID partners list`
- `pinterest-api-tool business-access --business-id BUSINESS_ID asset-members --asset-id ASSET_ID`
- `pinterest-api-tool business-access --business-id BUSINESS_ID asset-partners --asset-id ASSET_ID`
- `pinterest-api-tool business-access --business-id BUSINESS_ID member-assets --member-id MEMBER_ID`
- `pinterest-api-tool business-access --business-id BUSINESS_ID partner-assets --partner-id PARTNER_ID`

Notes:
- List commands support pagination via `--limit`, `--page-size`, and `--bookmark`.
- Use `--param key=value` to pass through supported filters for a specific endpoint.

## Resources / lookup (read-only)

- `pinterest-api-tool resources ad-account-countries`
- `pinterest-api-tool resources delivery-metrics`
- `pinterest-api-tool resources metrics-ready-state`
- `pinterest-api-tool resources targeting --targeting-type TARGETING_TYPE`
- `pinterest-api-tool resources interest --interest-id INTEREST_ID`

## Analytics

- `pinterest-api-tool analytics user`
- `pinterest-api-tool analytics top-pins [--sort-by IMPRESSION]`
- `pinterest-api-tool analytics top-video-pins [--sort-by IMPRESSION]`
- `pinterest-api-tool analytics pin --id PIN_ID`
- `pinterest-api-tool analytics pins --ids PIN_ID,PIN_ID`

Analytics defaults:
- Date range: last 90 days (`--start-date YYYY-MM-DD`, `--end-date YYYY-MM-DD`)
- Default metric: `IMPRESSION`

Useful analytics flags:
- `--metric IMPRESSION --metric OUTBOUND_CLICK` (repeatable)
- `--param key=value` (repeatable; passed through as a query param)

## Ads

These endpoints require access to a Pinterest ad account (and may require additional scopes/tiers).

Write commands are dry-run by default:
- Use `--apply --yes` to attempt apply. Current apply attempts require explicit no-snapshot approval before write.
- Any write that can increase spend requires `--ack-spend` before the refusal point.

- `pinterest-api-tool ads accounts list`
- `pinterest-api-tool ads accounts get --id AD_ACCOUNT_ID`
- `pinterest-api-tool ads campaigns list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads campaigns get --ad-account-id AD_ACCOUNT_ID --id CAMPAIGN_ID`
- `pinterest-api-tool ads campaigns create --ad-account-id AD_ACCOUNT_ID --body-file campaign_create.json`
- `pinterest-api-tool ads campaigns update --ad-account-id AD_ACCOUNT_ID --id CAMPAIGN_ID --body-file campaign_update.json`
- `pinterest-api-tool ads campaigns pause --ad-account-id AD_ACCOUNT_ID --id CAMPAIGN_ID`
- `pinterest-api-tool ads campaigns resume --ad-account-id AD_ACCOUNT_ID --id CAMPAIGN_ID`
- `pinterest-api-tool ads ad-groups list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads ad-groups get --ad-account-id AD_ACCOUNT_ID --id AD_GROUP_ID`
- `pinterest-api-tool ads ad-groups create --ad-account-id AD_ACCOUNT_ID --body-file ad_group_create.json`
- `pinterest-api-tool ads ad-groups update --ad-account-id AD_ACCOUNT_ID --id AD_GROUP_ID --body-file ad_group_update.json`
- `pinterest-api-tool ads ad-groups pause --ad-account-id AD_ACCOUNT_ID --id AD_GROUP_ID`
- `pinterest-api-tool ads ad-groups resume --ad-account-id AD_ACCOUNT_ID --id AD_GROUP_ID`
- `pinterest-api-tool ads ads list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads ads get --ad-account-id AD_ACCOUNT_ID --id AD_ID`
- `pinterest-api-tool ads ads create --ad-account-id AD_ACCOUNT_ID --body-file ad_create.json`
- `pinterest-api-tool ads ads update --ad-account-id AD_ACCOUNT_ID --id AD_ID --body-file ad_update.json`
- `pinterest-api-tool ads ads pause --ad-account-id AD_ACCOUNT_ID --id AD_ID`
- `pinterest-api-tool ads ads resume --ad-account-id AD_ACCOUNT_ID --id AD_ID`
- `pinterest-api-tool ads analytics ad-account --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads analytics campaigns --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads analytics ad-groups --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads analytics ads --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads analytics pins --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads targeting-analytics ad-account --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads targeting-analytics campaigns --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads targeting-analytics ad-groups --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads targeting-analytics ads --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads audience-insights --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads audiences --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads conversions tags list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads conversions tags get --ad-account-id AD_ACCOUNT_ID --id CONVERSION_TAG_ID`
- `pinterest-api-tool ads conversions page-visit --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads conversions ocpm-eligible --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads conversions eqs --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool ads reports create --ad-account-id AD_ACCOUNT_ID --body-file REQUEST.json` (requires `--apply --yes --ack-volume`, then requires explicit no-snapshot approval before report creation)
- `pinterest-api-tool ads reports get --ad-account-id AD_ACCOUNT_ID --token TOKEN`
- `pinterest-api-tool ads reports run --ad-account-id AD_ACCOUNT_ID --body-file REQUEST.json --out-dir OUT_DIR` (requires `--apply --yes --ack-volume`, then requires explicit no-snapshot approval before report creation, receipt, download, or output files)

Notes:
- List commands support pagination via `--limit`, `--page-size`, and `--bookmark`.
- Use `--param key=value` to pass through supported filters for a specific endpoint.
- Ads analytics defaults:
  - Date range: last 30 days (`--start-date YYYY-MM-DD`, `--end-date YYYY-MM-DD`)
  - Metrics: pass `--metric COLUMN_NAME` (repeatable) to set `columns=...`
  - Optional: pass `--granularity DAY|HOUR|...` (if supported by the endpoint)

## Jobs (batch write refusals)

- `pinterest-api-tool jobs run --file jobs.json --out-dir OUT_DIR` (requires `--apply --yes` for any remote-write row; `ads.reports.run` additionally requires `--ack-volume`; then requires explicit no-snapshot approval before receipts or summary output)

Job file formats:
- JSON: list of `{ "action": "...", ... }` or `{ "jobs": [ ... ] }`
- CSV: a table with an `action` column + additional columns for inputs

Supported actions:
- `ads.reports.run`
  - Required fields per row: `ad_account_id`, `body_file`
  - Optional caps: `max_poll_attempts`, `max_poll_seconds`, `poll_interval_s`, `max_download_bytes`

Future outputs under `OUT_DIR`:
- These outputs are reserved for future successful or failed processed rows.
- Current remote-write rows require explicit no-snapshot approval before `receipts/row-0001.json` or `summary.json` is written.

## Catalogs

Catalogs endpoints require access to a Pinterest ad account that owns the catalog.

- `pinterest-api-tool catalogs list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool catalogs create --body-file catalog_create.json [--ad-account-id AD_ACCOUNT_ID]`
- `pinterest-api-tool catalogs feeds list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool catalogs feeds get --ad-account-id AD_ACCOUNT_ID --id FEED_ID`
- `pinterest-api-tool catalogs feeds create --ad-account-id AD_ACCOUNT_ID --body-file feed_create.json`
- `pinterest-api-tool catalogs feeds update --ad-account-id AD_ACCOUNT_ID --id FEED_ID --body-file feed_update.json`
- `pinterest-api-tool catalogs feeds ingest --ad-account-id AD_ACCOUNT_ID --id FEED_ID` (requires `--apply --yes --ack-volume`, then requires explicit no-snapshot approval before write)
- `pinterest-api-tool catalogs feed-processing-results list --ad-account-id AD_ACCOUNT_ID --feed-id FEED_ID`
- `pinterest-api-tool catalogs product-groups list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool catalogs product-groups get --ad-account-id AD_ACCOUNT_ID --id PRODUCT_GROUP_ID`
- `pinterest-api-tool catalogs product-group-products list --ad-account-id AD_ACCOUNT_ID --product-group-id PRODUCT_GROUP_ID`
- `pinterest-api-tool catalogs item-issues list --processing-result-id PROCESSING_RESULT_ID [--ad-account-id AD_ACCOUNT_ID]`
- `pinterest-api-tool catalogs available-filter-values [--ad-account-id AD_ACCOUNT_ID]`
- `pinterest-api-tool catalogs product-group-product-counts --product-group-id PRODUCT_GROUP_ID [--ad-account-id AD_ACCOUNT_ID]`
- `pinterest-api-tool catalogs items-batch get --batch-id BATCH_ID [--ad-account-id AD_ACCOUNT_ID]`
- `pinterest-api-tool catalogs reports list --ad-account-id AD_ACCOUNT_ID`
- `pinterest-api-tool catalogs reports stats --ad-account-id AD_ACCOUNT_ID`

## Audit

- `pinterest-api-tool audit snapshot --out-dir OUT_DIR`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --skip-analytics`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --ad-account-id AD_ACCOUNT_ID --include-ads`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --ad-account-id AD_ACCOUNT_ID --include-catalogs`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --include-user-account`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --include-business-access --business-id BUSINESS_ID`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --include-resources`
- `pinterest-api-tool audit snapshot --out-dir OUT_DIR --ad-account-id AD_ACCOUNT_ID --include-conversions`

Snapshot outputs (written under `OUT_DIR`):
- `meta.json`: run metadata (time, base URL)
- `boards.json`: full boards list (paginated fetch)
- `board_sections_by_board.json`: sections list per board (best-effort; per-board errors recorded)
- `boards_summary.json`: board id/name/privacy + section counts (derived from the two files above)
- `pins.json`: full pins list (paginated fetch)
- `analytics_user.json`: account analytics (if enabled and permitted)
- `analytics_top_pins.json`: top pins analytics (if enabled and permitted)
- `analytics_top_video_pins.json`: top video pins analytics (if enabled and permitted)
- `ads/ad_accounts.json`: ad accounts list (if `--include-ads`)
- `ads/campaigns.json`: campaigns list for `--ad-account-id` (if `--include-ads`)
- `ads/ad_groups.json`: ad groups list for `--ad-account-id` (if `--include-ads`)
- `ads/ads.json`: ads list for `--ad-account-id` (if `--include-ads`)
- `ads/analytics/ad_account.json`: ad account analytics (best-effort; if `--include-ads`)
- `ads/analytics/campaigns.json`: campaigns analytics (best-effort; if `--include-ads`)
- `ads/analytics/ad_groups.json`: ad groups analytics (best-effort; if `--include-ads`)
- `ads/analytics/ads.json`: ads analytics (best-effort; if `--include-ads`)
- `ads/analytics/pins.json`: ad pins analytics (best-effort; if `--include-ads`)
- `ads/targeting_analytics/ad_account.json`: ad account targeting analytics (best-effort; if `--include-ads`)
- `ads/targeting_analytics/campaigns.json`: campaigns targeting analytics (best-effort; if `--include-ads`)
- `ads/targeting_analytics/ad_groups.json`: ad groups targeting analytics (best-effort; if `--include-ads`)
- `ads/targeting_analytics/ads.json`: ads targeting analytics (best-effort; if `--include-ads`)
- `ads/audience_insights.json`: audience insights (best-effort; if `--include-ads`)
- `ads/insights_audiences.json`: audience insights audiences (best-effort; if `--include-ads`)
- `catalogs/catalogs.json`: catalogs list for `--ad-account-id` (if `--include-catalogs`)
- `catalogs/feeds.json`: feeds list for `--ad-account-id` (if `--include-catalogs`)
- `catalogs/product_groups.json`: product groups list for `--ad-account-id` (if `--include-catalogs`)
- `catalogs/reports.json`: catalog reports list (best-effort; if `--include-catalogs`)
- `catalogs/reports_stats.json`: catalog report aggregated stats (best-effort; if `--include-catalogs`)
- `catalogs/feed_processing_results/`: one JSON file per feed id (best-effort; if `--include-catalogs`)
- `catalogs/item_issues/`: one JSON file per processing result id (best-effort; if `--include-catalogs`)
- `catalogs/product_group_products/`: one JSON file per product group id (best-effort; if `--include-catalogs`)
- `user_account/businesses.json`: user businesses list (if `--include-user-account`)
- `user_account/followers.json`: user followers list (if `--include-user-account`)
- `user_account/following.json`: user following list (if `--include-user-account`)
- `user_account/following_boards.json`: user following boards list (if `--include-user-account`)
- `user_account/websites.json`: user websites list (if `--include-user-account`)
- `user_account/websites_verification.json`: user websites verification (if `--include-user-account`)
- `business/assets.json`: business assets list (if `--include-business-access`)
- `business/members.json`: business members list (if `--include-business-access`)
- `business/partners.json`: business partners list (if `--include-business-access`)
- `business/asset_members/`: one JSON file per asset id (if `--include-business-access`)
- `business/asset_partners/`: one JSON file per asset id (if `--include-business-access`)
- `business/member_assets/`: one JSON file per member id (if `--include-business-access`)
- `business/partner_assets/`: one JSON file per partner id (if `--include-business-access`)
- `resources/ad_account_countries.json`: resources lookup (if `--include-resources`)
- `resources/delivery_metrics.json`: resources lookup (if `--include-resources`)
- `resources/metrics_ready_state.json`: resources lookup (if `--include-resources`)
- `conversions/tags.json`: conversion tags list (if `--include-conversions`)
- `conversions/page_visit.json`: conversion tags page visit (if `--include-conversions`)
- `conversions/ocpm_eligible.json`: conversion tags oCPM eligible (if `--include-conversions`)
- `conversions/eqs.json`: conversion EQS (if `--include-conversions`)

Notes:
- Snapshot treats analytics errors as warnings; core inventory errors are fatal.
- Use `--skip-analytics` if analytics endpoints are not available for your app/scopes.
- Ads/catalogs exports are best-effort and warning-only; use `--export-limit` / `--export-page-size` to bound volume.
