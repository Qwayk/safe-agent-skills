# Save a Meta Ads snapshot

Use a snapshot when you need the campaign, ad, creative, and reporting tables together. Start with the smallest [preset](presets_reference.md) that covers your work. Use `ecom_core` for sales reporting or `leadgen_core` for lead reporting.

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_123456 \
  --preset ecom_core \
  --since 2026-01-01 --until 2026-01-07 \
  --extra-insights-breakdown-table placement:publisher_platform,platform_position \
  --out-dir ./exports
```

Choose the account, dates and export folder before running it. The placement option adds a table beside the main report. It keeps Facebook Feed and Instagram Stories as separate rows even when they have the same ad and date. Omit the extra-table option for an export without that placement split.

## Check what you got

Open the path shown in `snapshot_export.manifest_path`. The file lists the tables, row counts, join keys, and requests. A request can stop at a page or item limit. Check `partial_success`, `requests[].incomplete_reason`, and `errors` before summing the rows. Use `--strict` if a failed table request should stop the export.

Each table in `tables/` is JSONL, with one record per line. Match ads to creatives by `creative_id`. For insights, use the account, report object, dates, and any breakdown columns named in the manifest. The placement table includes `publisher_platform` and `platform_position` in its row keys.

Use `--since` with `--until` or use `--date-preset` for a period like `last_7d`. Add `--insights-time-increment 1` for daily rows. The [command guide](command_reference.md) lists the other fields, filters, and limits you can set.

## Saved files

- `manifest.json` lists the account, preset, requests, tables, asset downloads, and errors.
- `tables/` holds the result tables and the creative summaries and links built from the returned data.
- `.state/runs/` holds the local audit file and run index.

Creative asset downloads are optional. Pass `--download-assets` to save files under `assets/`. Use `--assets-overwrite` to decide what happens if a file is already there. Check each download’s result in `tables/assets.jsonl` when you enable it.
