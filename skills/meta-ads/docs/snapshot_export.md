# Snapshot export (analysis pack)

`snapshot export` produces an analysis-ready folder pack containing:

- `manifest.json` (schema + join keys + request/error inventory)
- `tables/*.jsonl` (normalized tables; one JSON object per line)

This tool is **GET-only**. The snapshot export does not mutate anything in Meta Ads.

## Command

```bash
meta-ads-api-tool snapshot export \
  --ad-account-id act_<id> \
  --preset maximal_firehose \
  --out-dir ./exports \
  --run-id 2026-02-05T000000Z \
  --max-pages 50 \
  --max-items 0
```

Notes:
- If `--run-id` is omitted, the tool generates one (time-based).
- The export is **partial-success by default**: if one chunk fails (permissions/fields), the export continues and records the error in `manifest.json`.
- Add `--strict` to fail the export if any chunk fails.
- Creative asset downloads are **opt-in** via `--download-assets` and only run when enabled.
- The export also writes a few **local-only derived tables** (no extra API calls): `creative_anatomy.jsonl` and `asset_urls.jsonl`.

## Folder layout

Under `--out-dir`, the tool creates:

```
meta_ads_snapshot_<run_id>/
  manifest.json
  tables/
    campaigns.jsonl
    ad_sets.jsonl
    ads.jsonl
    creatives.jsonl
    creative_anatomy.jsonl  # derived locally from creatives payloads
    asset_urls.jsonl        # derived locally; URLs are token-redacted
    insights.jsonl
    insights_<suffix>.jsonl # optional: created by --extra-insights-breakdown-table (repeatable)
    assets.jsonl          # only when --download-assets is enabled (may be empty)
  assets/                 # only when --download-assets is enabled
```

## Snapshot insights controls (recommended)

Most “winning ads” analysis is time-bounded. Prefer setting an explicit time range:

- `--since YYYY-MM-DD --until YYYY-MM-DD` → sets `time_range` (overrides preset/`--param`)
- `--date-preset <name>` (example: `last_7d`, `last_28d`) → sets `date_preset` (overrides preset/`--param`)

Additional optional overrides (apply to all insights tables in the pack):

- `--insights-time-increment <val>`
- `--insights-breakdown <name> ...`
- `--insights-action-breakdown <val> ...`
- `--insights-action-attribution-window <val> ...`

## Extra insights breakdown tables (optional)

Use `--extra-insights-breakdown-table` to add additional insights tables without losing your base table.

Example: add placement and age/gender breakdown tables:

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset maximal_firehose \
  --since 2026-01-01 --until 2026-01-31 \
  --extra-insights-breakdown-table placement:publisher_platform,platform_position \
  --extra-insights-breakdown-table demo:age,gender \
  --out-dir ./exports
```

## Manifest schema (high level)

`manifest.json` is a JSON object with these top-level keys:

- `schema_version` (currently `"1"`)
- `tool` (`name`, `version`)
- `run` (`run_id`, `started_at_utc`, `finished_at_utc`)
- `env` (`base_url`, `api_version`, `ad_account_id`)
- `preset` (`preset_id`, `preset_schema_version`)
- `join_keys` (table → list of join key names)
- `tables` (table inventory: `table`, `relpath`, `rows`)
- `assets` (asset download inventory + counts; URLs are redacted)
- `requests` (sanitized request summaries; never includes tokens)
- `errors` (structured errors; partial-success uses this to record gaps)

## Join keys

Join keys are duplicated into each row (in addition to the raw fields) to make joins easy.

Current join keys by table:

- `campaigns`: `ad_account_id`, `campaign_id`
- `ad_sets`: `ad_account_id`, `adset_id`, `campaign_id`
- `ads`: `ad_account_id`, `ad_id`, `adset_id`, `campaign_id`, `creative_id`
- `creatives`: `ad_account_id`, `creative_id`
- `creative_anatomy`: `ad_account_id`, `creative_id`
- `asset_urls`: `ad_account_id`, `creative_id`, `url_sha256`
- `insights`: `ad_account_id`, `ad_id`, `date_start`, `date_stop`
- `insights_<suffix>`: same as `insights`
- `assets`: `ad_account_id`, `creative_id`, `url_sha256`

## `.state/` run artifacts

Each `snapshot export` run also writes local proof artifacts under:

- `.state/runs/<run_id>/audit.jsonl` (per-run sanitized audit log)
- `.state/runs/index.jsonl` (append-only run index)

These files are gitignored and are designed for local debugging and verification.

## Asset downloads (optional)

If you enable `--download-assets`, the export will:

- Extract candidate creative asset URLs (when present in the creative payload)
- Download them into `assets/` (filenames are derived from a SHA-256 prefix of the URL; no path traversal)
- Record successes/skips/failures in `tables/assets.jsonl` and `manifest.json`

Safety notes:
- Downloads are **never** performed unless `--download-assets` is set.
- Overwrites are controlled by `--assets-overwrite never|if_missing|always`.
- Any `access_token` query param is redacted (`***REDACTED***`) before being written to JSON outputs.
