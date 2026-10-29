# Media buyer quickstart (optional export workflow)

Direct GAQL is available without this export sequence. This optional workflow exports a stable, joinable Google Ads optimization pack you (and an AI agent) can use to diagnose delivery, keyword quality, RSA strength, tracking setup, and recommendation pressure without GAQL.

Snapshot export is read-only to Google Ads. The tool also supports explicit RPC write methods (plan-first), but this quickstart focuses on safe exports:
- consume quota, and
- write local files (your export pack) when you explicitly apply.

If you want exact command syntax and flags, also see `docs/command_reference.md`.

## 1) Pick a preset for the export

Start with:
- `optimization_pack_v1` (account-review tables)
- `analysis_pack_max_v1` (maximal; use when you want “everything”)
- `analysis_pack_v1` (older minimal starter)

Run:
- `google-ads-api-tool presets list`
- `google-ads-api-tool presets show --preset optimization_pack_v1`
- `google-ads-api-tool presets show --preset analysis_pack_v2`
- `google-ads-api-tool presets show --preset analysis_pack_max_v1`

## 2) Export a pack (dry-run first)

Dry-run (no API calls; no pack folder is written):
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack`

Apply (calls the Google Ads API and writes local pack files):
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes`

Include optional groups (recommended for deeper analysis; may increase time/quota):
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes --include-optional`

Temp implementation audit path (writes only the pack, not run history beside the env file):
- `google-ads-api-tool --no-artifacts snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./tmp/google-ads-pack --apply --yes --include-optional`

If you re-run to the same `--out-dir`, add `--overwrite`.

## 3) Open the pack and confirm it’s complete

Inside your `--out-dir`:
- `manifest.json` is the index (what’s available, counts, warnings, and where errors were recorded).
- `tables/*.jsonl` are the datasets (one JSON object per line).
- `tables/creative_anatomy.jsonl` is a derived table that normalizes ad creative (best-effort).
- `queries/queries.json` records the exact queries that were executed.
- `errors/errors.jsonl` records per-group failures (if any).

If the export had partial failures, the pack is still usable. The manifest will show which tables are missing or incomplete.

## 4) How to join tables (the practical way)

Use the pack’s `manifest.json`:
- `join_map` explains which join keys exist and what they mean.
- Each table entry includes `join_keys` and a `row_count`.

Typical joins:
- Join performance (`ad_daily_metrics`) to creative (`creative_anatomy`) using:
  - `customer.id`
  - `ad_group_ad.resource_name` and/or `ad.id`

If you’re using a spreadsheet or a notebook, start by loading:
- `tables/ad_daily_metrics.jsonl`
- `tables/creative_anatomy.jsonl`

Then group by creative (resource name or ad id) and compute “winners” for your date range.

## 5) Interpret the evidence

Choose questions from the user's decision and the underlying data. Verify current mechanics with official sources and distinguish correlation from cause. Use direct GAQL for any useful field; it does not require exhausting presets first. Legacy `snapshot analyze diagnose` and `optimize` remain for compatibility, but their heuristics are not verified account conclusions or a required stage.

## 7) What to do next (safe)

If your goal is “find winning ads,” go to:
- `docs/winning_ads_workbook.md`

If you want an AI agent to do the analysis without you learning the tables:
- `docs/agent_recipes.md`

If you need a very specific query that isn’t covered by presets:
- use `google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT campaign.id, campaign.name FROM campaign LIMIT 5" --limit 5` for a small sample; omit both limits for complete query results.
