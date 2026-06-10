# KPI dictionary (what each metric means)

This page is designed for both:
- non-technical media buyers (what you’re looking at), and
- AI agents (which tables/fields answer which questions).

Important rule:
- These exports are descriptive. Do not make causal claims from them.

## Core raw metrics (most common)

You will see these in several tables (example: `tables/ad_daily_metrics.jsonl`):

- `metrics.impressions`: how many times an ad was shown.
- `metrics.clicks`: how many clicks were recorded.
- `metrics.cost_micros`: spend in micros (1,000,000 micros = 1 unit of currency).
- `metrics.conversions`: conversions attributed to the chosen conversion settings.
- `metrics.conversions_value`: the “value” of those conversions (when configured).

Optimization metrics you will also see in `optimization_pack_v1`:
- `metrics.search_impression_share`
- `metrics.search_budget_lost_impression_share`
- `metrics.search_rank_lost_impression_share`
- `metrics.search_exact_match_impression_share`
- `metrics.search_top_impression_share`
- `metrics.search_absolute_top_impression_share`
- `ad_group_criterion.quality_info.quality_score`
- `ad_group_criterion.quality_info.search_predicted_ctr`
- `ad_group_criterion.quality_info.creative_quality_score`
- `ad_group_criterion.quality_info.post_click_quality_score`
- `ad_group_ad.ad_strength`
- `customer.optimization_score`
- `campaign.optimization_score`

## Derived KPIs (computed by the agent; not exported)

These are not exported directly. The agent computes them from raw metrics:

- `CTR` = `clicks / impressions`
- `CPC` = `cost / clicks`
- `CPM` = `cost / impressions * 1000`
- `CVR` = `conversions / clicks`
- `CPA` = `cost / conversions`
- `ROAS` = `conversions_value / cost`

Guardrails (important):
- If the denominator is 0, treat the KPI as “unknown” (do not divide by zero).
- Prefer filtering out very small samples before ranking winners.

## “Winning ads” (the safest definition)

Start from:
- `tables/ad_daily_metrics.jsonl` (performance)
- `tables/creative_anatomy.jsonl` (what the ad says / where it sends traffic)

Join keys (use `manifest.json` as the main reference):
- `customer.id`
- `ad_group_ad.resource_name` and/or `ad.id`

## Optional deep-diagnosis tables (only if exported with `--include-optional`)

Depending on the preset, you may also get:

- `tables/ad_daily_metrics_by_device.jsonl`: break performance by device (`segments.device`).
- `tables/ad_daily_metrics_by_network.jsonl`: break performance by network (`segments.ad_network_type`).
- `tables/ad_daily_metrics_by_hour.jsonl`: break performance by hour (`segments.hour`).
- `tables/ad_daily_metrics_by_day_of_week.jsonl`: break performance by day-of-week (`segments.day_of_week`).
- `tables/ad_daily_metrics_by_country.jsonl`: break performance by country (`segments.geo_target_country`).
- `tables/ad_daily_metrics_by_region.jsonl`: break performance by region (`segments.geo_target_region`).
- `tables/ad_daily_metrics_by_city.jsonl`: break performance by city (`segments.geo_target_city`).
- `tables/ad_daily_metrics_by_gender.jsonl`: break performance by gender (`segments.gender`).
- `tables/ad_daily_metrics_by_age_range.jsonl`: break performance by age range (`segments.age_range`).
- `tables/ad_daily_conversions_by_action.jsonl`: break conversions by conversion action (`segments.conversion_action`).
- `tables/search_terms_daily.jsonl`: search terms by day (where available).
- `tables/keyword_daily_metrics.jsonl`: keyword performance by day.
- `tables/landing_pages_daily.jsonl`: landing page URL performance.
- `tables/placements_daily.jsonl`: placement performance (can be large).
- `tables/rsa_asset_performance.jsonl`: Responsive Search Ad asset labels (where available).
- `tables/asset_groups.jsonl`, `tables/asset_group_assets.jsonl`, `tables/assets.jsonl`: Performance Max asset context.

## “Why is this ad winning?” (data-first checklist)

For a specific winning ad:
1) Confirm it’s a real winner (volume + KPI):
   - `ad_daily_metrics` → compute CPA/ROAS/CTR/CVR, then rank.
2) Read the creative anatomy:
   - `creative_anatomy` headlines/descriptions/final_urls.
3) Check context:
   - campaign channel type + ad group type (from `campaigns` + `ad_groups`).
4) Look for segmentation clues (optional tables):
   - device, hour, day-of-week, network.
5) Confirm what “conversion” means in this account:
   - use conversion-action breakdowns if present (`ad_daily_conversions_by_action`).

## Optimization interpretation shortcuts

- High `search_budget_lost_impression_share` with low rank loss usually means budget pressure first.
- High `search_rank_lost_impression_share` with low budget loss usually means Ad Rank or relevance pressure first.
- Low `quality_score` or `BELOW_AVERAGE` quality components usually point to search intent, ad relevance, or landing-page mismatch.
- Weak RSA `ad_strength` is a prompt to review asset coverage and message range, not to auto-apply Google suggestions.
- Low `optimization_score` is context only. Review the recommendation types before deciding whether any action is worth planning.
