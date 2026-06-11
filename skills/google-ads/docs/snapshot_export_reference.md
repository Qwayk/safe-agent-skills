# Snapshot export reference (analysis pack contract)

This document defines the pack layout and semantics produced by:
- `google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack`

It also covers local-only pack diffs:
- `google-ads-api-tool snapshot compare --pack-a ./out/pack_a --pack-b ./out/pack_b --out-dir ./out/compare`

Snapshot export is read-only to Google Ads. The output files are local analysis artifacts, useful for review and proof. It is still "risky" in the sense that it can:
- consume API quota, and
- write local files (packs, run artifacts).

Export files are not connected to any built-in account restore or rollback flow.

## Safety model

- Default: dry-run (no API calls, no pack folder written).
- Apply: requires `--apply --yes` and writes a local pack folder.
- Optional groups: by default, only `required=true` preset groups are exported. Pass `--include-optional` to also export `required=false` groups.
- Partial success: default behavior; failed groups are recorded and the export continues.
- Strict mode: `--strict` fails (exit code 1) if any required group fails, but still writes pack artifacts for auditability.

## Output folder layout

When applied, the `--out-dir` contains:
- `manifest.json` (index + join map + counts + warnings)
- `tables/*.jsonl` (one JSON object per line)
- `queries/queries.json` (executed queries)
- `errors/errors.jsonl` (per-group errors)

Derived table:
- `tables/creative_anatomy.jsonl` (best-effort normalization; always present, may be empty)

Typical optimization tables in `optimization_pack_v1`:
- `customer_overview`
- `campaign_inventory`
- `campaign_settings`
- `campaign_budgets`
- `campaign_pressure_daily`
- `ad_group_inventory`
- `ad_group_ads`
- `ad_daily_metrics`
- `keyword_daily_metrics`
- `keyword_quality_snapshot`
- `search_terms_daily`
- `conversion_actions`
- `recommendations`

Optional optimization tables:
- `rsa_asset_performance`
- `landing_pages_daily`
- `placements_daily`
- `ad_daily_metrics_by_device`
- `ad_daily_metrics_by_network`
- `ad_daily_metrics_by_hour`
- `ad_daily_conversions_by_action`

## manifest.json (required fields)

Top level:
- `schema_version` (integer)
- `tool` and `tool_version`
- `generated_at_utc`
- `preset`, `customer_id`, `since`, `until`, `segmentation`
- `join_map` (copied from the preset)
- `tables[]` (one entry per exported or derived table)
- `groups[]` (one entry per query group)
- `warnings[]`
- `errors_path` and `queries_path`

`tables[]` entries:
- `name`, `path`, `row_count`, `truncated`, `join_keys`, `source_group_id`

`groups[]` entries:
- `group_id`, `required`, `status` (`ok` or `failed`), `error_count`, `row_count`, `truncated`

## errors/errors.jsonl

Each line is a JSON object with:
- `ts_utc`
- `group_id`
- `required`
- `error_type`
- `error` (secrets redacted)

## Truncation and explosion controls

To keep exports bounded:
- `--max-rows` caps rows per group output and records `truncated=true` plus a warning.
- `--page-size` controls API page size.
- `--segmentation` is bounded by preset template variants (no arbitrary segments injection).

## snapshot compare

Dry-run:
- emits a JSON plan summary and does not write files.

Apply:
- requires `--apply`
- writes `compare_summary.json` to `--out-dir`
- output is descriptive only (no causal claims)
