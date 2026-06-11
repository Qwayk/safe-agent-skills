# Presets reference

Presets are versioned JSON files that define:
- query groups (what gets exported),
- stable output filenames,
- join keys for each table,
- bounded template variants (for segmentation),
- and placeholder requirements (`{customer_id}`, `{since}`, `{until}`).

Commands:
- `google-ads-api-tool presets list`
- `google-ads-api-tool presets show --preset analysis_pack_v1`
- `google-ads-api-tool presets show --preset optimization_pack_v1`
- `google-ads-api-tool presets show --preset analysis_pack_v2`
- `google-ads-api-tool presets validate`

## Built-in presets

### optimization_pack_v1 (recommended)

Purpose:
- Search-first optimization export for agents that need diagnosis-ready campaign pressure, keyword quality, RSA strength, conversion-action context, and recommendation inventory without ad-hoc GAQL.

Query groups (required vs optional):

| group_id | required | output table | Use |
|---|---:|---|---|
| `customer_overview` | yes | `tables/customer_overview.jsonl` | account state, optimization score |
| `campaign_inventory` | yes | `tables/campaign_inventory.jsonl` | campaign identity, primary status, optimization score |
| `campaign_settings` | yes | `tables/campaign_settings.jsonl` | channel, bidding, network and serving settings |
| `campaign_budgets` | yes | `tables/campaign_budgets.jsonl` | campaign budgets and delivery state |
| `campaign_pressure_daily` | yes | `tables/campaign_pressure_daily.jsonl` | impression share, lost IS rank/budget, top share |
| `ad_group_inventory` | yes | `tables/ad_group_inventory.jsonl` | ad group state and type |
| `ad_group_ads` | yes | `tables/ad_group_ads.jsonl` | ad status, RSA strength, policy summary |
| `ad_daily_metrics` | yes | `tables/ad_daily_metrics.jsonl` | core ad performance |
| `keyword_daily_metrics` | yes | `tables/keyword_daily_metrics.jsonl` | keyword performance |
| `keyword_quality_snapshot` | yes | `tables/keyword_quality_snapshot.jsonl` | Quality Score and components |
| `search_terms_daily` | yes | `tables/search_terms_daily.jsonl` | negative-keyword and intent cleanup |
| `conversion_actions` | yes | `tables/conversion_actions.jsonl` | primary/secondary conversion setup |
| `recommendations` | yes | `tables/recommendations.jsonl` | native recommendation inventory |
| `rsa_asset_performance` | no | `tables/rsa_asset_performance.jsonl` | asset labels for weak RSAs |
| `landing_pages_daily` | no | `tables/landing_pages_daily.jsonl` | post-click waste review |
| `placements_daily` | no | `tables/placements_daily.jsonl` | placement waste review |
| `ad_daily_metrics_by_device` | no | `tables/ad_daily_metrics_by_device.jsonl` | device context |
| `ad_daily_metrics_by_network` | no | `tables/ad_daily_metrics_by_network.jsonl` | network context |
| `ad_daily_metrics_by_hour` | no | `tables/ad_daily_metrics_by_hour.jsonl` | hour context |
| `ad_daily_conversions_by_action` | no | `tables/ad_daily_conversions_by_action.jsonl` | conversion-action breakdown |

Important required fields:
- Quality Score and components
- RSA `ad_strength`
- account and campaign `optimization_score`
- search impression share
- lost impression share by budget and rank
- exact match impression share
- top and absolute top impression share
- recommendation rows
- conversion-action primary/secondary context

Export behavior:
- By default, `snapshot export` runs only `required=yes` groups.
- Use `--include-optional` when you need RSA asset labels, landing pages, placements, or segmentation context.

### analysis_pack_v2

Purpose:
- future-proof “analysis pack” export for exploring cross-channel winners using core joins plus optional search term, keyword, device, and PMax asset context.

Query groups (required vs optional):

| group_id | required | output table | Join keys (high level) |
|---|---:|---|---|
| campaigns | yes | `tables/campaigns.jsonl` | customer + campaign |
| ad_groups | yes | `tables/ad_groups.jsonl` | customer + campaign + ad_group |
| ad_group_ads | yes | `tables/ad_group_ads.jsonl` | customer + campaign + ad_group + ad_group_ad + ad |
| ad_daily_metrics | yes | `tables/ad_daily_metrics.jsonl` | customer + campaign + ad_group + ad_group_ad + ad + date |
| ad_daily_metrics_by_device | no | `tables/ad_daily_metrics_by_device.jsonl` | base keys + date + device |
| search_terms_daily | no | `tables/search_terms_daily.jsonl` | customer + campaign + ad_group + date + search_term |
| keyword_daily_metrics | no | `tables/keyword_daily_metrics.jsonl` | base keys + date + keyword |
| asset_groups | no | `tables/asset_groups.jsonl` | customer + campaign + asset_group (PMax) |
| asset_group_assets | no | `tables/asset_group_assets.jsonl` | customer + campaign + asset_group + asset |
| assets | no | `tables/assets.jsonl` | asset resource_name + type |

Export behavior:
- By default, `snapshot export` runs only `required=yes` groups.
- To also export optional groups, pass `--include-optional`.

Derived tables (local-only; no extra API calls):
- `tables/creative_anatomy.jsonl`

Template variants:
- `base` only (as of tool version 0.5.x)

Placeholders:
- Some query groups require `{since}` and `{until}` (metrics/segments).
- Some groups are inventory-only (they do not require a date range).

## Join keys: the main reference

The preset’s `join_map` is copied into the pack manifest:
- open `manifest.json` → `join_map`
- use that map to join tables deterministically

### analysis_pack_max_v1 (maximal)

Purpose:
- Deep diagnosis and “explain why it wins” using extra segmentation and context:
  - network / hour / day-of-week breakdowns,
  - geo and demographic breakdowns (where available),
  - conversion-action breakdowns,
  - landing pages,
  - placements (often huge),
  - RSA asset performance labels (where available),
  - budgets and campaign settings.

Export behavior:
- By default, only `required=yes` groups are exported.
- To get the full “firehose”, export with `--include-optional`.

Note:
- Some optional tables may fail on some accounts (permissions, feature availability, or API limits). That is expected; errors are recorded in `errors/errors.jsonl`.
- For geo and demographic tables, the preset uses the dedicated GAQL views (`geographic_view`, `gender_view`, `age_range_view`) rather than unsupported `segments.*` fields.

### analysis_pack_v1 (older minimal starter)

Purpose:
- smaller starter “analysis pack” export (core entities + daily performance by ad).
