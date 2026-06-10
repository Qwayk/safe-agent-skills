# Winning ads workbook (GET-only)

Use this workbook to find “winning” ads, understand why they win, and generate safe optimization/recreation guidance.

This tool is **GET-only** (read-only). It does not create, update, or pause ads.

## A) Define “winning”

Pick a definition that matches your objective:

- **Efficiency winners:** lowest CPA / highest ROAS at stable volume
- **Scale winners:** high conversion volume with acceptable CPA
- **Hook winners:** high CTR / low CPC (top-of-funnel)
- **Creative fatigue:** declining CTR/CVR over time while spend holds

Write your definition down first; the same dataset supports multiple lenses.

## B) Export a snapshot pack

Start with `ecom_core` unless you specifically need many fields.

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --since 2026-01-01 --until 2026-01-31 \
  --out-dir ./exports
```

Open `manifest.json` and confirm:
- `errors` is empty or acceptable (partial-success is common with large fieldsets)
- The expected tables exist under `tables/`

Optional: add extra breakdown tables (without changing your base insights table):

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --since 2026-01-01 --until 2026-01-31 \
  --extra-insights-breakdown-table placement:publisher_platform,platform_position \
  --out-dir ./exports
```

## C) Pull a focused insights slice

Example: ad-level daily performance with actions and spend.

```bash
meta-ads-api-tool --output json insights get \
  --ad-account-id act_<id> \
  --level ad \
  --fields ad_id,date_start,date_stop,impressions,clicks,spend,actions,action_values \
  --since 2026-01-01 --until 2026-01-31 \
  --time-increment 1
```

Tips:
- Use `--time-increment 1` for daily rows; omit it for aggregate rows.
- Use `--breakdown` for dimensions like `age`, `gender`, `country`, `platform_position` (where supported).

## D) Compare two ranges

This is the fastest way to detect fatigue, promotions, or targeting changes.

```bash
meta-ads-api-tool --output json insights compare \
  --ad-account-id act_<id> \
  --level ad \
  --fields ad_id,impressions,clicks,spend,actions \
  --since-a 2026-01-01 --until-a 2026-01-07 \
  --since-b 2026-01-08 --until-b 2026-01-14
```

## E) Inspect the creative

Once you identify a winning `creative_id`:

```bash
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

Use the anatomy output to answer:
- What’s the primary offer and CTA?
- What’s the landing URL (token-redacted)?
- Are there multiple headlines/bodies (dynamic creative)?

## F) Join keys for analysis

Snapshot packs include join keys in every table row. Common joins:

- `ads.creative_id` ↔ `creatives.creative_id`
- `insights.ad_id` ↔ `ads.ad_id`
- `ad_sets.campaign_id` ↔ `campaigns.campaign_id`

See `docs/snapshot_export.md` for the authoritative join key list.
