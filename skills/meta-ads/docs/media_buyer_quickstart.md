# Media-buyer quickstart (GET-only)

This tool is a **read-only**, **GET-only** Meta Ads “data firehose”. It’s designed to export analysis-ready snapshot packs and help you inspect creatives without needing custom scripts.

## 1) Pick a preset

List presets:

```bash
meta-ads-api-tool --output json presets list
```

Most users start with:
- `ecom_core` (smaller, faster)
- `maximal_firehose` (largest; more fields; more likely to hit permission gaps)
- `creative_fatigue_daily` (daily diagnostics; includes rankings)

Show details:

```bash
meta-ads-api-tool --output json presets show --preset ecom_core
```

## 2) Export a snapshot pack

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --since 2026-01-01 --until 2026-01-31 \
  --out-dir ./exports \
  --max-pages 50
```

Outputs:
- `manifest.json` (what was fetched + what failed)
- `tables/*.jsonl` (analysis-ready tables; one JSON object per line)

Notes:
- The pack also includes `tables/creative_anatomy.jsonl` and `tables/asset_urls.jsonl` (derived locally; no extra API calls).

Optional: enable partial-success hard-fail:

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset maximal_firehose \
  --out-dir ./exports \
  --strict
```

Optional: download creative asset URLs (only if present in the creative payload):

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --out-dir ./exports \
  --download-assets \
  --assets-overwrite if_missing
```

## 3) Compare two date ranges (same settings)

Example: compare last week vs the week before at the ad level:

```bash
meta-ads-api-tool --output json insights compare \
  --ad-account-id act_<id> \
  --level ad \
  --fields ad_id,impressions,clicks,spend,actions \
  --since-a 2026-01-01 --until-a 2026-01-07 \
  --since-b 2026-01-08 --until-b 2026-01-14 \
  --time-increment 1
```

## 4) Inspect a creative (anatomy + previews)

Anatomy (normalized “what this creative is”):

```bash
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
```

Preview HTML (placement preview):

```bash
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

Notes:
- Previews can return HTML snippets; treat them as untrusted content if you render them.
- Any `access_token` query param is redacted in stdout JSON.
