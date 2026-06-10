# API coverage (endpoints -> CLI)

## Summary

- Provider: TikTok for Business Marketing API
- API base URL: `https://business-api.tiktok.com`
- Manifest: `docs/official_operations_v1_2026-05-24.json`
- Manifest generated at UTC: `2026-05-24T07:01:08Z`
- Total operations in pinned manifest: `240`
- Auth style: `Access-Token` header + app credentials

## Coverage target

- Implemented CLI surface: `api` (one parser command for each operation), `api ops list`, and `api ops show`.
- Coverage policy used here:
  - `Status = implemented`
  - `Safety status = live-unverified / access-gated`

Writes in this tool are blocked unless `--live`, `--apply`, `--yes`, `--plan-in`, and `--ack-irreversible` are present. After those gates pass, current writes still require explicit no-snapshot approval before provider HTTP when no saved snapshot is available.

## Family counts from pinned manifest

| Family | Count |
|---|---|
| `ad` | 8 |
| `adgroup` | 5 |
| `advertiser` | 4 |
| `app` | 6 |
| `audience` | 1 |
| `bc` | 37 |
| `blockedword` | 7 |
| `campaign` | 12 |
| `catalog` | 27 |
| `comment` | 7 |
| `creative` | 8 |
| `discovery` | 2 |
| `dmp` | 17 |
| `file` | 5 |
| `gmv-max` | 10 |
| `identity` | 3 |
| `oauth2` | 2 |
| `offline` | 4 |
| `optimizer` | 7 |
| `pangle-audience-package` | 1 |
| `pangle-block-list` | 2 |
| `pixel` | 9 |
| `playable` | 5 |
| `report` | 4 |
| `search` | 1 |
| `smart-plus` | 18 |
| `term` | 3 |
| `tool` | 25 |


## Endpoint coverage

| Family | Operation command | Method | Path | CLI form | Safety gates | Status | Notes |
|---|---|---|---|---|---|---|---|
| ad | `ad-aco-create` | POST | `/open_api/v1.3/ad/aco/create/` | `api ad-aco-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| ad | `ad-aco-get` | GET | `/open_api/v1.3/ad/aco/get/` | `api ad-aco-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| ad | `ad-aco-material-status-update` | POST | `/open_api/v1.3/ad/aco/material_status/update/` | `api ad-aco-material-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| ad | `ad-aco-update` | POST | `/open_api/v1.3/ad/aco/update/` | `api ad-aco-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| ad | `ad-create` | POST | `/open_api/v1.3/ad/create/` | `api ad-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| ad | `ad-get` | GET | `/open_api/v1.3/ad/get/` | `api ad-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| ad | `ad-status-update` | POST | `/open_api/v1.3/ad/status/update/` | `api ad-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| ad | `ad-update` | POST | `/open_api/v1.3/ad/update/` | `api ad-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| adgroup | `adgroup-create` | POST | `/open_api/v1.3/adgroup/create/` | `api adgroup-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| adgroup | `adgroup-get` | GET | `/open_api/v1.3/adgroup/get/` | `api adgroup-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| adgroup | `adgroup-quota` | GET | `/open_api/v1.3/adgroup/quota/` | `api adgroup-quota` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| adgroup | `adgroup-status-update` | POST | `/open_api/v1.3/adgroup/status/update/` | `api adgroup-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| adgroup | `adgroup-update` | POST | `/open_api/v1.3/adgroup/update/` | `api adgroup-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| advertiser | `advertiser-balance-get` | GET | `/open_api/v1.3/advertiser/balance/get/` | `api advertiser-balance-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| advertiser | `advertiser-info` | GET | `/open_api/v1.3/advertiser/info/` | `api advertiser-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| advertiser | `advertiser-transaction-get` | GET | `/open_api/v1.3/advertiser/transaction/get/` | `api advertiser-transaction-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| advertiser | `advertiser-update` | POST | `/open_api/v1.3/advertiser/update/` | `api advertiser-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| app | `app-create` | POST | `/open_api/v1.3/app/create/` | `api app-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| app | `app-info` | GET | `/open_api/v1.3/app/info/` | `api app-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| app | `app-list` | GET | `/open_api/v1.3/app/list/` | `api app-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| app | `app-optimization-event` | GET | `/open_api/v1.3/app/optimization_event/` | `api app-optimization-event` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| app | `app-optimization-event-retargeting` | GET | `/open_api/v1.3/app/optimization_event/retargeting/` | `api app-optimization-event-retargeting` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| app | `app-update` | POST | `/open_api/v1.3/app/update/` | `api app-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| audience | `audience-insight-overlap` | GET | `/open_api/v1.3/audience/insight/overlap/` | `api audience-insight-overlap` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-account-transaction-get` | GET | `/open_api/v1.3/bc/account/transaction/get/` | `api bc-account-transaction-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-advertiser-create` | POST | `/open_api/v1.3/bc/advertiser/create/` | `api bc-advertiser-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-admin-delete` | POST | `/open_api/v1.3/bc/asset/admin/delete/` | `api bc-asset-admin-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-admin-get` | GET | `/open_api/v1.3/bc/asset/admin/get/` | `api bc-asset-admin-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-assign` | POST | `/open_api/v1.3/bc/asset/assign/` | `api bc-asset-assign` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-get` | GET | `/open_api/v1.3/bc/asset/get/` | `api bc-asset-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-group-create` | POST | `/open_api/v1.3/bc/asset_group/create/` | `api bc-asset-group-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-group-delete` | POST | `/open_api/v1.3/bc/asset_group/delete/` | `api bc-asset-group-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-group-get` | GET | `/open_api/v1.3/bc/asset_group/get/` | `api bc-asset-group-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-group-list` | GET | `/open_api/v1.3/bc/asset_group/list/` | `api bc-asset-group-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-group-update` | POST | `/open_api/v1.3/bc/asset_group/update/` | `api bc-asset-group-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-asset-member-get` | GET | `/open_api/v1.3/bc/asset/member/get/` | `api bc-asset-member-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-partner-get` | GET | `/open_api/v1.3/bc/asset/partner/get/` | `api bc-asset-partner-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-asset-unassign` | POST | `/open_api/v1.3/bc/asset/unassign/` | `api bc-asset-unassign` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-balance-get` | GET | `/open_api/v1.3/bc/balance/get/` | `api bc-balance-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-billing-group-create` | POST | `/open_api/v1.3/bc/billing_group/create/` | `api bc-billing-group-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-billing-group-get` | GET | `/open_api/v1.3/bc/billing_group/get/` | `api bc-billing-group-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-billing-group-update` | POST | `/open_api/v1.3/bc/billing_group/update/` | `api bc-billing-group-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-create` | POST | `/open_api/v1.3/bc/create/` | `api bc-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-get` | GET | `/open_api/v1.3/bc/get/` | `api bc-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-image-upload` | POST | `/open_api/v1.3/bc/image/upload/` | `api bc-image-upload` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-invoice-unpaid-get` | GET | `/open_api/v1.3/bc/invoice/unpaid/get/` | `api bc-invoice-unpaid-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-member-assign` | POST | `/open_api/v1.3/bc/member/assign/` | `api bc-member-assign` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-member-delete` | POST | `/open_api/v1.3/bc/member/delete/` | `api bc-member-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-member-get` | GET | `/open_api/v1.3/bc/member/get/` | `api bc-member-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-member-invite` | POST | `/open_api/v1.3/bc/member/invite/` | `api bc-member-invite` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-member-update` | POST | `/open_api/v1.3/bc/member/update/` | `api bc-member-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-partner-add` | POST | `/open_api/v1.3/bc/partner/add/` | `api bc-partner-add` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-partner-asset-delete` | POST | `/open_api/v1.3/bc/partner/asset/delete/` | `api bc-partner-asset-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-partner-asset-get` | GET | `/open_api/v1.3/bc/partner/asset/get/` | `api bc-partner-asset-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-partner-delete` | POST | `/open_api/v1.3/bc/partner/delete/` | `api bc-partner-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-partner-get` | GET | `/open_api/v1.3/bc/partner/get/` | `api bc-partner-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-pixel-link-get` | GET | `/open_api/v1.3/bc/pixel/link/get/` | `api bc-pixel-link-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-pixel-link-update` | POST | `/open_api/v1.3/bc/pixel/link/update/` | `api bc-pixel-link-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-pixel-transfer` | POST | `/open_api/v1.3/bc/pixel/transfer/` | `api bc-pixel-transfer` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| bc | `bc-transaction-get` | GET | `/open_api/v1.3/bc/transaction/get/` | `api bc-transaction-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| bc | `bc-transfer` | POST | `/open_api/v1.3/bc/transfer/` | `api bc-transfer` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-check` | GET | `/open_api/v1.3/blockedword/check/` | `api blockedword-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-create` | POST | `/open_api/v1.3/blockedword/create/` | `api blockedword-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-delete` | POST | `/open_api/v1.3/blockedword/delete/` | `api blockedword-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-list` | GET | `/open_api/v1.3/blockedword/list/` | `api blockedword-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-task-check` | GET | `/open_api/v1.3/blockedword/task/check/` | `api blockedword-task-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-task-create` | POST | `/open_api/v1.3/blockedword/task/create/` | `api blockedword-task-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| blockedword | `blockedword-update` | POST | `/open_api/v1.3/blockedword/update/` | `api blockedword-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-create` | POST | `/open_api/v1.3/campaign/create/` | `api campaign-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-get` | GET | `/open_api/v1.3/campaign/get/` | `api campaign-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-create` | POST | `/open_api/v1.3/campaign/gmv_max/create/` | `api campaign-gmv-max-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-info` | GET | `/open_api/v1.3/campaign/gmv_max/info/` | `api campaign-gmv-max-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-session-create` | POST | `/open_api/v1.3/campaign/gmv_max/session/create/` | `api campaign-gmv-max-session-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-session-delete` | POST | `/open_api/v1.3/campaign/gmv_max/session/delete/` | `api campaign-gmv-max-session-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-session-get` | GET | `/open_api/v1.3/campaign/gmv_max/session/get/` | `api campaign-gmv-max-session-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-session-list` | GET | `/open_api/v1.3/campaign/gmv_max/session/list/` | `api campaign-gmv-max-session-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-session-update` | POST | `/open_api/v1.3/campaign/gmv_max/session/update/` | `api campaign-gmv-max-session-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-gmv-max-update` | POST | `/open_api/v1.3/campaign/gmv_max/update/` | `api campaign-gmv-max-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-status-update` | POST | `/open_api/v1.3/campaign/status/update/` | `api campaign-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| campaign | `campaign-update` | POST | `/open_api/v1.3/campaign/update/` | `api campaign-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-available-country-get` | GET | `/open_api/v1.3/catalog/available_country/get/` | `api catalog-available-country-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-capitalize` | POST | `/open_api/v1.3/catalog/capitalize/` | `api catalog-capitalize` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-create` | POST | `/open_api/v1.3/catalog/create/` | `api catalog-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-delete` | POST | `/open_api/v1.3/catalog/delete/` | `api catalog-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-eventsource-bind` | POST | `/open_api/v1.3/catalog/eventsource/bind/` | `api catalog-eventsource-bind` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-eventsource-bind-get` | GET | `/open_api/v1.3/catalog/eventsource_bind/get/` | `api catalog-eventsource-bind-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-eventsource-unbind` | POST | `/open_api/v1.3/catalog/eventsource/unbind/` | `api catalog-eventsource-unbind` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-feed-create` | POST | `/open_api/v1.3/catalog/feed/create/` | `api catalog-feed-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-feed-delete` | POST | `/open_api/v1.3/catalog/feed/delete/` | `api catalog-feed-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-feed-get` | GET | `/open_api/v1.3/catalog/feed/get/` | `api catalog-feed-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-feed-log` | GET | `/open_api/v1.3/catalog/feed/log/` | `api catalog-feed-log` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-feed-update` | POST | `/open_api/v1.3/catalog/feed/update/` | `api catalog-feed-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-get` | GET | `/open_api/v1.3/catalog/get/` | `api catalog-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-lexicon-get` | GET | `/open_api/v1.3/catalog/lexicon/get/` | `api catalog-lexicon-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-location-currency-get` | GET | `/open_api/v1.3/catalog/location_currency/get/` | `api catalog-location-currency-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-overview` | GET | `/open_api/v1.3/catalog/overview/` | `api catalog-overview` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-product-delete` | POST | `/open_api/v1.3/catalog/product/delete/` | `api catalog-product-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-product-file` | POST | `/open_api/v1.3/catalog/product/file/` | `api catalog-product-file` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-product-log` | GET | `/open_api/v1.3/catalog/product/log/` | `api catalog-product-log` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-set-delete` | POST | `/open_api/v1.3/catalog/set/delete/` | `api catalog-set-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-set-get` | GET | `/open_api/v1.3/catalog/set/get/` | `api catalog-set-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-set-product-get` | GET | `/open_api/v1.3/catalog/set/product/get/` | `api catalog-set-product-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| catalog | `catalog-set-update` | POST | `/open_api/v1.3/catalog/set/update/` | `api catalog-set-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-update` | POST | `/open_api/v1.3/catalog/update/` | `api catalog-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-video-delete` | POST | `/open_api/v1.3/catalog/video/delete/` | `api catalog-video-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-video-file` | POST | `/open_api/v1.3/catalog/video/file/` | `api catalog-video-file` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| catalog | `catalog-video-get` | GET | `/open_api/v1.3/catalog/video/get/` | `api catalog-video-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| comment | `comment-delete` | POST | `/open_api/v1.3/comment/delete/` | `api comment-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| comment | `comment-list` | GET | `/open_api/v1.3/comment/list/` | `api comment-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| comment | `comment-post` | POST | `/open_api/v1.3/comment/post/` | `api comment-post` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| comment | `comment-reference` | GET | `/open_api/v1.3/comment/reference/` | `api comment-reference` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| comment | `comment-status-update` | POST | `/open_api/v1.3/comment/status/update/` | `api comment-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| comment | `comment-task-check` | GET | `/open_api/v1.3/comment/task/check/` | `api comment-task-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| comment | `comment-task-create` | POST | `/open_api/v1.3/comment/task/create/` | `api comment-task-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-asset-delete` | POST | `/open_api/v1.3/creative/asset/delete/` | `api creative-asset-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-asset-share` | POST | `/open_api/v1.3/creative/asset/share/` | `api creative-asset-share` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-image-edit` | POST | `/open_api/v1.3/creative/image/edit/` | `api creative-image-edit` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-portfolio-create` | POST | `/open_api/v1.3/creative/portfolio/create/` | `api creative-portfolio-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-portfolio-get` | GET | `/open_api/v1.3/creative/portfolio/get/` | `api creative-portfolio-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| creative | `creative-portfolio-list` | GET | `/open_api/v1.3/creative/portfolio/list/` | `api creative-portfolio-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| creative | `creative-shareable-link-create` | POST | `/open_api/v1.3/creative/shareable_link/create/` | `api creative-shareable-link-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| creative | `creative-smart-text-generate` | POST | `/open_api/v1.3/creative/smart_text/generate/` | `api creative-smart-text-generate` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| discovery | `discovery-detail` | GET | `/open_api/v1.3/discovery/detail/` | `api discovery-detail` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| discovery | `discovery-trending-list` | GET | `/open_api/v1.3/discovery/trending_list/` | `api discovery-trending-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-apply` | POST | `/open_api/v1.3/dmp/custom_audience/apply/` | `api dmp-custom-audience-apply` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-apply-log` | GET | `/open_api/v1.3/dmp/custom_audience/apply/log/` | `api dmp-custom-audience-apply-log` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-create` | POST | `/open_api/v1.3/dmp/custom_audience/create/` | `api dmp-custom-audience-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-delete` | POST | `/open_api/v1.3/dmp/custom_audience/delete/` | `api dmp-custom-audience-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-file-upload` | POST | `/open_api/v1.3/dmp/custom_audience/file/upload/` | `api dmp-custom-audience-file-upload` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-get` | GET | `/open_api/v1.3/dmp/custom_audience/get/` | `api dmp-custom-audience-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-list` | GET | `/open_api/v1.3/dmp/custom_audience/list/` | `api dmp-custom-audience-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-lookalike-create` | POST | `/open_api/v1.3/dmp/custom_audience/lookalike/create/` | `api dmp-custom-audience-lookalike-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-lookalike-update` | POST | `/open_api/v1.3/dmp/custom_audience/lookalike/update/` | `api dmp-custom-audience-lookalike-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-rule-create` | POST | `/open_api/v1.3/dmp/custom_audience/rule/create/` | `api dmp-custom-audience-rule-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-share` | POST | `/open_api/v1.3/dmp/custom_audience/share/` | `api dmp-custom-audience-share` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-share-cancel` | POST | `/open_api/v1.3/dmp/custom_audience/share/cancel/` | `api dmp-custom-audience-share-cancel` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-share-log` | GET | `/open_api/v1.3/dmp/custom_audience/share/log/` | `api dmp-custom-audience-share-log` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| dmp | `dmp-custom-audience-update` | POST | `/open_api/v1.3/dmp/custom_audience/update/` | `api dmp-custom-audience-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-saved-audience-create` | POST | `/open_api/v1.3/dmp/saved_audience/create/` | `api dmp-saved-audience-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-saved-audience-delete` | POST | `/open_api/v1.3/dmp/saved_audience/delete/` | `api dmp-saved-audience-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| dmp | `dmp-saved-audience-list` | GET | `/open_api/v1.3/dmp/saved_audience/list/` | `api dmp-saved-audience-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| file | `ad-image-upload` | POST | `/open_api/v1.3/file/image/ad/upload/` | `api ad-image-upload` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| file | `ad-video-info` | GET | `/open_api/v1.3/file/video/ad/info/` | `api ad-video-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| file | `ad-video-search` | GET | `/open_api/v1.3/file/video/ad/search/` | `api ad-video-search` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| file | `ad-video-upload` | POST | `/open_api/v1.3/file/video/ad/upload/` | `api ad-video-upload` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| file | `file-image-ad-info` | GET | `/open_api/v1.3/file/image/ad/info/` | `api file-image-ad-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-bid-recommend` | GET | `/open_api/v1.3/gmv_max/bid/recommend/` | `api gmv-max-bid-recommend` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-custom-anchor-video-list-get` | GET | `/open_api/v1.3/gmv_max/custom_anchor_video_list/get/` | `api gmv-max-custom-anchor-video-list-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-exclusive-authorization-create` | POST | `/open_api/v1.3/gmv_max/exclusive_authorization/create/` | `api gmv-max-exclusive-authorization-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-exclusive-authorization-get` | GET | `/open_api/v1.3/gmv_max/exclusive_authorization/get/` | `api gmv-max-exclusive-authorization-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-identity-get` | GET | `/open_api/v1.3/gmv_max/identity/get/` | `api gmv-max-identity-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-occupied-custom-shop-ads-list` | GET | `/open_api/v1.3/gmv_max/occupied_custom_shop_ads/list/` | `api gmv-max-occupied-custom-shop-ads-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-report-get` | GET | `/open_api/v1.3/gmv_max/report/get/` | `api gmv-max-report-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-store-list` | GET | `/open_api/v1.3/gmv_max/store/list/` | `api gmv-max-store-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-store-shop-ad-usage-check` | GET | `/open_api/v1.3/gmv_max/store/shop_ad_usage_check/` | `api gmv-max-store-shop-ad-usage-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| gmv-max | `gmv-max-video-get` | GET | `/open_api/v1.3/gmv_max/video/get/` | `api gmv-max-video-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| identity | `identity-create` | POST | `/open_api/v1.3/identity/create/` | `api identity-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| identity | `identity-get` | GET | `/open_api/v1.3/identity/get/` | `api identity-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| identity | `identity-video-info` | GET | `/open_api/v1.3/identity/video/info/` | `api identity-video-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| oauth2 | `oauth2-access-token` | POST | `/open_api/v1.3/oauth2/access_token/` | `api oauth2-access-token` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| oauth2 | `oauth2-advertiser-get` | GET | `/open_api/v1.3/oauth2/advertiser/get/` | `api oauth2-advertiser-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| offline | `offline-create` | POST | `/open_api/v1.3/offline/create/` | `api offline-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| offline | `offline-delete` | POST | `/open_api/v1.3/offline/delete/` | `api offline-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| offline | `offline-get` | GET | `/open_api/v1.3/offline/get/` | `api offline-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| offline | `offline-update` | POST | `/open_api/v1.3/offline/update/` | `api offline-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-batch-bind` | POST | `/open_api/v1.3/optimizer/rule/batch_bind/` | `api optimizer-rule-batch-bind` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-create` | POST | `/open_api/v1.3/optimizer/rule/create/` | `api optimizer-rule-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-get` | GET | `/open_api/v1.3/optimizer/rule/get/` | `api optimizer-rule-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-list` | GET | `/open_api/v1.3/optimizer/rule/list/` | `api optimizer-rule-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-result-get` | GET | `/open_api/v1.3/optimizer/rule/result/get/` | `api optimizer-rule-result-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-result-list` | GET | `/open_api/v1.3/optimizer/rule/result/list/` | `api optimizer-rule-result-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| optimizer | `optimizer-rule-update` | POST | `/open_api/v1.3/optimizer/rule/update/` | `api optimizer-rule-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pangle-audience-package | `pangle-audience-package-get` | GET | `/open_api/v1.3/pangle_audience_package/get/` | `api pangle-audience-package-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| pangle-block-list | `pangle-block-list-get` | GET | `/open_api/v1.3/pangle_block_list/get/` | `api pangle-block-list-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| pangle-block-list | `pangle-block-list-update` | POST | `/open_api/v1.3/pangle_block_list/update/` | `api pangle-block-list-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-batch` | POST | `/open_api/v1.3/pixel/batch/` | `api pixel-batch` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-create` | POST | `/open_api/v1.3/pixel/create/` | `api pixel-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-event-create` | POST | `/open_api/v1.3/pixel/event/create/` | `api pixel-event-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-event-delete` | POST | `/open_api/v1.3/pixel/event/delete/` | `api pixel-event-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-event-stats` | GET | `/open_api/v1.3/pixel/event/stats/` | `api pixel-event-stats` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| pixel | `pixel-event-update` | POST | `/open_api/v1.3/pixel/event/update/` | `api pixel-event-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-list` | GET | `/open_api/v1.3/pixel/list/` | `api pixel-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| pixel | `pixel-track` | POST | `/open_api/v1.3/pixel/track/` | `api pixel-track` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| pixel | `pixel-update` | POST | `/open_api/v1.3/pixel/update/` | `api pixel-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| playable | `playable-delete` | POST | `/open_api/v1.3/playable/delete/` | `api playable-delete` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| playable | `playable-get` | GET | `/open_api/v1.3/playable/get/` | `api playable-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| playable | `playable-save` | POST | `/open_api/v1.3/playable/save/` | `api playable-save` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| playable | `playable-upload` | POST | `/open_api/v1.3/playable/upload/` | `api playable-upload` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| playable | `playable-validate` | GET | `/open_api/v1.3/playable/validate/` | `api playable-validate` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| report | `report-integrated-get` | GET | `/open_api/v1.3/report/integrated/get/` | `api report-integrated-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| report | `report-task-cancel` | POST | `/open_api/v1.3/report/task/cancel/` | `api report-task-cancel` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| report | `report-task-check` | GET | `/open_api/v1.3/report/task/check/` | `api report-task-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| report | `report-task-create` | POST | `/open_api/v1.3/report/task/create/` | `api report-task-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| search | `search-region` | GET | `/open_api/v1.3/search/region/` | `api search-region` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-appeal` | POST | `/open_api/v1.3/smart_plus/ad/appeal/` | `api smart-plus-ad-appeal` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-create` | POST | `/open_api/v1.3/smart_plus/ad/create/` | `api smart-plus-ad-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-get` | GET | `/open_api/v1.3/smart_plus/ad/get/` | `api smart-plus-ad-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-material-status-update` | POST | `/open_api/v1.3/smart_plus/ad/material_status/update/` | `api smart-plus-ad-material-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-review-info` | GET | `/open_api/v1.3/smart_plus/ad/review_info/` | `api smart-plus-ad-review-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-status-update` | POST | `/open_api/v1.3/smart_plus/ad/status/update/` | `api smart-plus-ad-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-ad-update` | POST | `/open_api/v1.3/smart_plus/ad/update/` | `api smart-plus-ad-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-adgroup-create` | POST | `/open_api/v1.3/smart_plus/adgroup/create/` | `api smart-plus-adgroup-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-adgroup-get` | GET | `/open_api/v1.3/smart_plus/adgroup/get/` | `api smart-plus-adgroup-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-adgroup-status-update` | POST | `/open_api/v1.3/smart_plus/adgroup/status/update/` | `api smart-plus-adgroup-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-adgroup-update` | POST | `/open_api/v1.3/smart_plus/adgroup/update/` | `api smart-plus-adgroup-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-campaign-create` | POST | `/open_api/v1.3/smart_plus/campaign/create/` | `api smart-plus-campaign-create` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-campaign-get` | GET | `/open_api/v1.3/smart_plus/campaign/get/` | `api smart-plus-campaign-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-campaign-status-update` | POST | `/open_api/v1.3/smart_plus/campaign/status/update/` | `api smart-plus-campaign-status-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-campaign-update` | POST | `/open_api/v1.3/smart_plus/campaign/update/` | `api smart-plus-campaign-update` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-material-report-breakdown` | GET | `/open_api/v1.3/smart_plus/material_report/breakdown/` | `api smart-plus-material-report-breakdown` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-material-report-overview` | GET | `/open_api/v1.3/smart_plus/material_report/overview/` | `api smart-plus-material-report-overview` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| smart-plus | `smart-plus-material-review-info` | GET | `/open_api/v1.3/smart_plus/material/review_info/` | `api smart-plus-material-review-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| term | `term-check` | GET | `/open_api/v1.3/term/check/` | `api term-check` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| term | `term-confirm` | POST | `/open_api/v1.3/term/confirm/` | `api term-confirm` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| term | `term-get` | GET | `/open_api/v1.3/term/get/` | `api term-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-action-category` | GET | `/open_api/v1.3/tool/action_category/` | `api tool-action-category` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-bid-recommend` | POST | `/open_api/v1.3/tool/bid/recommend/` | `api tool-bid-recommend` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| tool | `tool-brand-safety-partner-authorize-status` | GET | `/open_api/v1.3/tool/brand_safety/partner/authorize/status/` | `api tool-brand-safety-partner-authorize-status` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-carrier` | GET | `/open_api/v1.3/tool/carrier/` | `api tool-carrier` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-contextual-tag-get` | GET | `/open_api/v1.3/tool/contextual_tag/get/` | `api tool-contextual-tag-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-contextual-tag-info` | GET | `/open_api/v1.3/tool/contextual_tag/info/` | `api tool-contextual-tag-info` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-device-model` | GET | `/open_api/v1.3/tool/device_model/` | `api tool-device-model` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-diagnosis-search-health` | GET | `/open_api/v1.3/tool/diagnosis/search/health/` | `api tool-diagnosis-search-health` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-hashtag-get` | GET | `/open_api/v1.3/tool/hashtag/get/` | `api tool-hashtag-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-hashtag-recommend` | GET | `/open_api/v1.3/tool/hashtag/recommend/` | `api tool-hashtag-recommend` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-interest-category` | GET | `/open_api/v1.3/tool/interest_category/` | `api tool-interest-category` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-interest-keyword-get` | GET | `/open_api/v1.3/tool/interest_keyword/get/` | `api tool-interest-keyword-get` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-interest-keyword-recommend` | GET | `/open_api/v1.3/tool/interest_keyword/recommend/` | `api tool-interest-keyword-recommend` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-language` | GET | `/open_api/v1.3/tool/language/` | `api tool-language` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-open-url` | GET | `/open_api/v1.3/tool/open_url/` | `api tool-open-url` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-os-version` | GET | `/open_api/v1.3/tool/os_version/` | `api tool-os-version` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-phone-region-code` | GET | `/open_api/v1.3/tool/phone_region_code/` | `api tool-phone-region-code` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-region` | GET | `/open_api/v1.3/tool/region/` | `api tool-region` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-targeting-category-recommend` | POST | `/open_api/v1.3/tool/targeting_category/recommend/` | `api tool-targeting-category-recommend` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| tool | `tool-targeting-info` | POST | `/open_api/v1.3/tool/targeting/info/` | `api tool-targeting-info` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| tool | `tool-targeting-list` | GET | `/open_api/v1.3/tool/targeting/list/` | `api tool-targeting-list` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-targeting-search` | POST | `/open_api/v1.3/tool/targeting/search/` | `api tool-targeting-search` | write (requires --live --apply --yes --plan-in --ack-irreversible) | implemented | live-unverified / access-gated |
| tool | `tool-timezone` | GET | `/open_api/v1.3/tool/timezone/` | `api tool-timezone` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-url-validate` | GET | `/open_api/v1.3/tool/url_validate/` | `api tool-url-validate` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |
| tool | `tool-vbo-status` | GET | `/open_api/v1.3/tool/vbo_status/` | `api tool-vbo-status` | read-only (live-required for execute; default plan) | implemented | live-unverified / access-gated |

## Known gaps

- None for manifest-surface coverage: all `240` pinned operations are wired to CLI command entries.
- Runtime calls are intentionally access-gated for live execution and write operations.
