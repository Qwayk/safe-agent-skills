# Winning ads workbook (how to use the pack)

Purpose:
- Identify “winners” using metrics and guardrails.
- Explain winners using creative anatomy (headlines/descriptions/URLs) plus segmentation context.

Rule (important):
- This workbook is descriptive. Do not make causal claims (“X caused Y”) from these exports.

## Tables you’ll use most

- `tables/ad_daily_metrics.jsonl` (daily performance by ad)
- `tables/creative_anatomy.jsonl` (normalized creative, best-effort)
- `tables/ad_group_ads.jsonl` (raw ad_group_ad rows)
- `tables/campaigns.jsonl` and `tables/ad_groups.jsonl` (context)

Optional tables (only present if you exported with `--include-optional`):
- `tables/search_terms_daily.jsonl` (search terms by day, when available)
- `tables/keyword_daily_metrics.jsonl` (keyword performance by day, when available)
- `tables/ad_daily_metrics_by_device.jsonl` (device breakdown by day)
- `tables/asset_groups.jsonl`, `tables/asset_group_assets.jsonl`, `tables/assets.jsonl` (Performance Max asset context)

## A simple “winner” definition (start here)

Pick a date range you trust (enough spend and enough conversions to be meaningful), then:

1) Filter to ads with non-trivial volume:
   - impressions and clicks are not tiny
   - conversions (or conversion value) is not 0
2) Rank by your primary goal metric:
   - conversions, conversion value, CPA (derived from cost / conversions), or ROAS (derived from value / cost)
3) Apply sanity checks:
   - exclude obvious outliers caused by tracking mistakes
   - ensure the ad ran for multiple days (not a single-day spike)

## Channel sections (what to look for)

This preset is designed to be cross-channel-friendly, but creative extraction is best-effort and will vary by ad type.

### Search

Look for:
- stable conversions or conversion value over multiple days
- headlines/descriptions patterns in `creative_anatomy`

Notes:
- Responsive Search Ads usually have the richest text creative anatomy.

### Display

Look for:
- conversion value or conversion volume relative to cost
- URL patterns and any extractable text (may be sparse)

### Video

Look for:
- conversion outcomes (or view-through proxies only if you explicitly choose them)
- ensure you’re comparing similar audience targeting contexts

### Shopping and Performance Max

Core winners are still found by joining `ad_daily_metrics` → `creative_anatomy` (by `ad_group_ad.resource_name` and/or `ad.id`).

For deeper PMax context, export with `--include-optional` and use:
- `asset_groups` (what asset groups exist)
- `asset_group_assets` + `assets` (which assets are in each asset group)

Note: `creative_anatomy` includes best-effort asset references when these optional tables are present.

## “Explain why it wins” checklist (descriptive)

For each winner:
- What is the creative message?
  - headlines, descriptions, and destination URL(s)
- Where does it sit in structure?
  - campaign channel type and ad group type (from raw tables)
- What is the performance story over time?
  - daily metrics: does it stay strong or spike once?
- Any red flags?
  - very small sample size, sudden changes, partial failures, or truncation warnings

## Safe optimization guidance (what you can say)

Good:
- “This ad has the best conversion value per cost over the chosen window.”
- “These headline themes appear across multiple top-performing ads.”
- “The pack export shows partial success; treat missing tables as unknowns.”

Not allowed:
- “This creative caused the performance.”
- “If you copy this, you’ll get the same results.”
