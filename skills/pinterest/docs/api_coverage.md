# API coverage

Last verified (UTC): 2026-02-03

Notes:
- The “Scopes” column is a reminder only. **Confirm required scopes in the Pinterest developer UI** (and the official docs), since scope names/requirements can change.
- Reference links point to the official Pinterest API v5 docs (operation IDs).
- Write coverage is split into:
  - : read-only surfaces (inventory + analytics + ads/catalog reads).
  - : safety-gated write plans and blocked apply refusals (plan → explicit attempt → require explicit no-snapshot approval before write).

## Inventory + account

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `auth check` | `GET /user_account` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/get |
| `user-account get` | `GET /user_account` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/get |
| `user-account businesses` | `GET /user_account/businesses` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/businesses |
| `user-account followers` | `GET /user_account/followers` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/followers |
| `user-account following` | `GET /user_account/following` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/following |
| `user-account following-boards` | `GET /user_account/following/boards` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/following/boards |
| `user-account websites list` | `GET /user_account/websites` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/websites |
| `user-account websites verification` | `GET /user_account/websites/verification` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/websites/verification |
| `boards list` | `GET /boards` | `boards:read` | https://developers.pinterest.com/docs/api/v5/#operation/boards/list |
| `boards get` | `GET /boards/{board_id}` | `boards:read` | https://developers.pinterest.com/docs/api/v5/#operation/boards/get |
| `board-sections list` | `GET /boards/{board_id}/sections` | `boards:read` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list |
| `board-pins list` | `GET /boards/{board_id}/pins` | `boards:read`, `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/boards/list_pins |
| `board-pins list --section-id ...` | `GET /boards/{board_id}/sections/{section_id}/pins` | `boards:read`, `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list_pins |
| `pins list` | `GET /pins` | `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/pins/list |
| `pins get` | `GET /pins/{pin_id}` | `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/pins/get |

## Business Access (read-only)

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `business-access --business-id ... assets list` | `GET /businesses/{business_id}/assets` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/assets |
| `business-access --business-id ... members list` | `GET /businesses/{business_id}/members` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/members |
| `business-access --business-id ... asset-members --asset-id ...` | `GET /businesses/{business_id}/assets/{asset_id}/members` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/asset_members |
| `business-access --business-id ... asset-partners --asset-id ...` | `GET /businesses/{business_id}/assets/{asset_id}/partners` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/asset_partners |
| `business-access --business-id ... member-assets --member-id ...` | `GET /businesses/{business_id}/members/{member_id}/assets` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/member_assets |
| `business-access --business-id ... partners list` | `GET /businesses/{business_id}/partners` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/partners |
| `business-access --business-id ... partner-assets --partner-id ...` | `GET /businesses/{business_id}/partners/{partner_id}/assets` | Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/business_access/partner_assets |

## Resources / lookup (read-only)

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `resources ad-account-countries` | `GET /resources/ad_account_countries` | N/A (lookup) | https://developers.pinterest.com/docs/api/v5/#operation/resources/ad_account_countries |
| `resources delivery-metrics` | `GET /resources/delivery_metrics` | N/A (lookup) | https://developers.pinterest.com/docs/api/v5/#operation/resources/delivery_metrics |
| `resources metrics-ready-state` | `GET /resources/metrics_ready_state` | N/A (lookup) | https://developers.pinterest.com/docs/api/v5/#operation/resources/metrics_ready_state |
| `resources targeting --targeting-type ...` | `GET /resources/targeting/{targeting_type}` | N/A (lookup) | https://developers.pinterest.com/docs/api/v5/#operation/resources/targeting |
| `resources interest --interest-id ...` | `GET /resources/targeting/interests/{interest_id}` | N/A (lookup) | https://developers.pinterest.com/docs/api/v5/#operation/resources/targeting/interests |

## Analytics

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `analytics user` | `GET /user_account/analytics` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics |
| `analytics top-pins` | `GET /user_account/analytics/top_pins` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics/top_pins |
| `analytics top-video-pins` | `GET /user_account/analytics/top_video_pins` | `user_accounts:read` | https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics/top_video_pins |
| `analytics pin --id ...` | `GET /pins/{pin_id}/analytics` | `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/pins/analytics |
| `analytics pins --ids ...` | `GET /pins/analytics` | `pins:read` | https://developers.pinterest.com/docs/api/v5/#operation/multi_pins/analytics |

## Ads

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `ads accounts list` | `GET /ad_accounts` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/list |
| `ads accounts get --id ...` | `GET /ad_accounts/{ad_account_id}` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/get |
| `ads campaigns list --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/campaigns` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list |
| `ads campaigns get --ad-account-id ... --id ...` | `GET /ad_accounts/{ad_account_id}/campaigns/{campaign_id}` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/get |
| `ads campaigns create --ad-account-id ...` | `POST /ad_accounts/{ad_account_id}/campaigns` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/create |
| `ads campaigns update --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/campaigns` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/update |
| `ads campaigns pause --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/campaigns` | `ads:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/update |
| `ads campaigns resume --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/campaigns` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/update |
| `ads ad-groups list --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ad_groups` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/list |
| `ads ad-groups get --ad-account-id ... --id ...` | `GET /ad_accounts/{ad_account_id}/ad_groups/{ad_group_id}` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/get |
| `ads ad-groups create --ad-account-id ...` | `POST /ad_accounts/{ad_account_id}/ad_groups` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/create |
| `ads ad-groups update --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ad_groups` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/update |
| `ads ad-groups pause --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ad_groups` | `ads:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/update |
| `ads ad-groups resume --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ad_groups` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/update |
| `ads ads list --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ads` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ads/list |
| `ads ads get --ad-account-id ... --id ...` | `GET /ad_accounts/{ad_account_id}/ads/{ad_id}` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ads/get |
| `ads ads create --ad-account-id ...` | `POST /ad_accounts/{ad_account_id}/ads` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ads/create |
| `ads ads update --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ads` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ads/update |
| `ads ads pause --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ads` | `ads:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/ads/update |
| `ads ads resume --ad-account-id ... --id ...` | `PATCH /ad_accounts/{ad_account_id}/ads` | `ads:write` + Business Access roles (varies); `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ads/update |
| `ads analytics ad-account --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics |
| `ads analytics campaigns --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/campaigns/analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/analytics |
| `ads analytics ad-groups --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ad_groups/analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics |
| `ads analytics ads --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ads/analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics |
| `ads analytics pins --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/pins/analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_pins/analytics |
| `ads targeting-analytics ad-account --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/targeting_analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/targeting_analytics/ad_account |
| `ads targeting-analytics campaigns --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/campaigns/targeting_analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/targeting_analytics/campaigns |
| `ads targeting-analytics ad-groups --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ad_groups/targeting_analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/targeting_analytics/ad_groups |
| `ads targeting-analytics ads --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/ads/targeting_analytics` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/targeting_analytics/ads |
| `ads audience-insights --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/audience_insights` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/ad_account/audience_insights |
| `ads audiences --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/insights/audiences` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/insights/audiences |
| `ads conversions tags list --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/conversion_tags` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/conversion_tags/list |
| `ads conversions tags get --ad-account-id ... --id ...` | `GET /ad_accounts/{ad_account_id}/conversion_tags/{conversion_tag_id}` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/conversion_tags/get |
| `ads conversions page-visit --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/conversion_tags/page_visit` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/conversion_tags/page_visit |
| `ads conversions ocpm-eligible --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/conversion_tags/ocpm_eligible` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/conversion_tags/ocpm_eligible |
| `ads conversions eqs --ad-account-id ...` | `GET /ad_accounts/{ad_account_id}/conversion_eqs` | Ads scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/conversion_eqs/get |

## Catalogs

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `catalogs list --ad-account-id ...` | `GET /catalogs` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs/list |
| `catalogs create` | `POST /catalogs` | `catalogs:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/catalogs/create |
| `catalogs feeds list --ad-account-id ...` | `GET /catalogs/feeds` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/feeds/list |
| `catalogs feeds get --ad-account-id ... --id ...` | `GET /catalogs/feeds/{feed_id}` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/feeds/get |
| `catalogs feeds create --ad-account-id ...` | `POST /catalogs/feeds` | `catalogs:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/feeds/create |
| `catalogs feeds update --ad-account-id ... --id ...` | `PATCH /catalogs/feeds/{feed_id}` | `catalogs:write` + Business Access roles (varies); `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/feeds/update |
| `catalogs feeds ingest --ad-account-id ... --id ...` | `POST /catalogs/feeds/{feed_id}/ingest` | `catalogs:write` + Business Access roles (varies); `--apply --yes --ack-volume` | https://developers.pinterest.com/docs/api/v5/#operation/feeds/ingest |
| `catalogs feed-processing-results list --ad-account-id ... --feed-id ...` | `GET /catalogs/feeds/{feed_id}/processing_results` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/feed_processing_results/list |
| `catalogs product-groups list --ad-account-id ...` | `GET /catalogs/product_groups` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_product_groups/list |
| `catalogs product-groups get --ad-account-id ... --id ...` | `GET /catalogs/product_groups/{product_group_id}` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_product_groups/get |
| `catalogs product-group-products list --ad-account-id ... --product-group-id ...` | `GET /catalogs/product_groups/{product_group_id}/products` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_product_group_pins/list |
| `catalogs item-issues list --processing-result-id ...` | `GET /catalogs/processing_results/{processing_result_id}/item_issues` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/items_issues/list |
| `catalogs available-filter-values` | `GET /catalogs/available_filter_values` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs/available_filter_values |
| `catalogs product-group-product-counts --product-group-id ...` | `GET /catalogs/product_groups/{product_group_id}/product_counts` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_product_groups/product_counts |
| `catalogs items-batch get --batch-id ...` | `GET /catalogs/items/batch/{batch_id}` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs/items/batch/get |
| `catalogs reports list --ad-account-id ...` | `GET /catalogs/reports` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_reports/list |
| `catalogs reports stats --ad-account-id ...` | `GET /catalogs/reports/stats` | Catalogs/shopping scopes + Business Access roles (varies) | https://developers.pinterest.com/docs/api/v5/#operation/catalogs_reports/stats |

## Token exchange (OAuth)

| CLI command | Method + path | Scopes (confirm in Pinterest developer UI) | Reference |
|---|---|---|---|
| `auth code exchange ...` | `POST /oauth/token` | Currently requires explicit no-snapshot approval before token exchange or local token writes | https://developers.pinterest.com/docs/api/v5/#operation/oauth/token |
| `auth login ...` | Browser consent URL + `POST /oauth/token` + `GET /user_account` | Currently requires explicit no-snapshot approval before token exchange or local token writes | https://developers.pinterest.com/docs/getting-started/authentication/ |

## Local-only outputs (no Pinterest API writes)

| CLI command | Writes | Notes |
|---|---|---|
| `audit snapshot --out-dir ...` | Local JSON files | Reads multiple inventory + analytics endpoints and writes snapshots to disk. |
| `pins links plan --pins-json ... --out ...` | Local JSON file | Builds a plan file from a prior `audit snapshot` `pins.json`. |

## Pinterest write workflow (safety gated)

| CLI command | Method + path | Safety contract | Reference |
|---|---|---|---|
| `pins links apply --plan ...` | Dry-run: `GET /pins/{pin_id}` preview. Apply attempt: requires explicit no-snapshot approval before `PATCH /pins/{pin_id}`. | Dry-run preview includes a before-state contract that requires explicit no-snapshot approval; confirmed apply requires `--apply --yes`, then requires explicit no-snapshot approval before write. | https://developers.pinterest.com/docs/api/v5/#operation/pins/update |

## — Writes (planned/implemented)

Safety model (all commands in this section):
- Dry-run by default (prints a deterministic plan or read-only preview; no remote writes).
- Any remote write attempt requires `--apply --yes`.
- Destructive operations additionally require `--ack-irreversible`.
- Commands that can increase ad spend additionally require `--ack-spend`.
- Commands that can trigger significant remote work additionally require `--ack-volume`.
- Current apply attempts require explicit no-snapshot approval before provider writes, local token writes, report receipts/downloads, job output, or successful write receipts.

| CLI command | Method + path | Safety gates | Reference | Status |
|---|---|---|---|---|
| `boards create --name ...` | `POST /boards` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/boards/create | Implemented + Tested |
| `boards update --id ...` | `PATCH /boards/{board_id}` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/boards/update | Implemented + Tested |
| `boards delete --id ...` | `DELETE /boards/{board_id}` | `--apply --yes --ack-irreversible` | https://developers.pinterest.com/docs/api/v5/#operation/boards/delete | Implemented + Tested |
| `boards ensure --name ...` | `GET /boards` → `POST /boards` or `PATCH /boards/{board_id}` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/boards/create | Implemented + Tested |
| `board-sections create --board-id ... --name ...` | `POST /boards/{board_id}/sections` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/create | Implemented + Tested |
| `board-sections update --board-id ... --section-id ... --name ...` | `PATCH /boards/{board_id}/sections/{section_id}` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/update | Implemented + Tested |
| `board-sections delete --board-id ... --section-id ...` | `DELETE /boards/{board_id}/sections/{section_id}` | `--apply --yes --ack-irreversible` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/delete | Implemented + Tested |
| `board-sections ensure --board-id ... --name ...` | `GET /boards/{board_id}/sections` → `POST /boards/{board_id}/sections` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/board_sections/create | Implemented + Tested |
| `pins create` / `pins update` / `pins delete` / `pins save` | various | `--apply --yes` (+ `--ack-irreversible` for delete) | https://developers.pinterest.com/docs/api/v5/#operation/pins/create | Implemented + Tested |
| `pins ensure` | list → create | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/pins/create | Implemented + Tested |
| `ads campaigns create/update` | `POST/PATCH /ad_accounts/{ad_account_id}/campaigns` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/create | Implemented + Tested |
| `ads campaigns pause` | `PATCH /ad_accounts/{ad_account_id}/campaigns` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/update | Implemented + Tested |
| `ads campaigns resume` | `PATCH /ad_accounts/{ad_account_id}/campaigns` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/campaigns/update | Implemented + Tested |
| `ads ad-groups create/update` | `POST/PATCH /ad_accounts/{ad_account_id}/ad_groups` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/create | Implemented + Tested |
| `ads ad-groups pause` | `PATCH /ad_accounts/{ad_account_id}/ad_groups` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/update | Implemented + Tested |
| `ads ad-groups resume` | `PATCH /ad_accounts/{ad_account_id}/ad_groups` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/update | Implemented + Tested |
| `ads ads create/update` | `POST/PATCH /ad_accounts/{ad_account_id}/ads` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ads/create | Implemented + Tested |
| `ads ads pause` | `PATCH /ad_accounts/{ad_account_id}/ads` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/ads/update | Implemented + Tested |
| `ads ads resume` | `PATCH /ad_accounts/{ad_account_id}/ads` | `--apply --yes --ack-spend` | https://developers.pinterest.com/docs/api/v5/#operation/ads/update | Implemented + Tested |
| `catalogs create` | `POST /catalogs` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/catalogs/create | Implemented + Tested |
| `catalogs update` | (not documented in API v5) | N/A | N/A | Not supported in v5 docs (as of 2026-02-03) |
| `catalogs feeds create/update` | `POST /catalogs/feeds; PATCH /catalogs/feeds/{feed_id}` | `--apply --yes` | https://developers.pinterest.com/docs/api/v5/#operation/feeds/create | Implemented + Tested |
| `catalogs feeds ingest` | `POST /catalogs/feeds/{feed_id}/ingest` | `--apply --yes --ack-volume` | https://developers.pinterest.com/docs/api/v5/#operation/feeds/ingest | Implemented + Tested |
| `ads reports create --ad-account-id ... --body-file ...` | `POST /ad_accounts/{ad_account_id}/reports` | `--apply --yes --ack-volume` | https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report | Implemented + Tested |
| `ads reports get --ad-account-id ... --token ...` | `GET /ad_accounts/{ad_account_id}/reports?token=...` | (read-only) | https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report | Implemented + Tested |
| `ads reports run --ad-account-id ... --body-file ... --out-dir ...` | `POST /ad_accounts/{ad_account_id}/reports` → poll `GET /ad_accounts/{ad_account_id}/reports?token=...` → download | `--apply --yes --ack-volume` + caps | https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report | Implemented + Tested |
| `jobs run --file ... --out-dir ...` | Batch runner (executes action rows, currently: `ads.reports.run`) | `--apply --yes` (+ `--ack-volume` for report jobs) | (tool internal) | Implemented + Tested |
