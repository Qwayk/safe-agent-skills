# Agent recipes (GET-only)

These recipes are written for AI agents (and humans) that want deterministic, parseable outputs.

Defaults:
- Use `--output json`
- Keep a sanitized audit log when helpful: `--log-file audit.jsonl`

## Recipe 1: Export an analysis pack (snapshot)

Goal: create a stable folder pack for downstream analysis.

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --since 2026-01-01 --until 2026-01-31 \
  --extra-insights-breakdown-table placement:publisher_platform,platform_position \
  --out-dir ./exports \
  --max-pages 50
```

Agent parsing tips:
- Read `snapshot_export.out_dir` and `snapshot_export.manifest_path`.
- Use `manifest.errors` + `manifest.requests` to detect partial-success and permission gaps.

## Recipe 2: Compare performance across two ranges

Goal: fetch two insights slices with identical settings (only `time_range` differs).

```bash
meta-ads-api-tool --output json insights compare \
  --ad-account-id act_<id> \
  --level ad \
  --fields ad_id,impressions,clicks,spend,actions \
  --since-a 2026-01-01 --until-a 2026-01-07 \
  --since-b 2026-01-08 --until-b 2026-01-14
```

Agent parsing tips:
- Output shape is one object with `data.a` and `data.b` plus shared metadata.
- Never assume identical row sets between ranges; treat missing rows as zeros if you compute deltas.

## Recipe 3: Creative anatomy (normalized extract)

Goal: turn a raw creative payload into a stable, normalized object for LLM reasoning.

```bash
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
```

Agent parsing tips:
- Prefer `anatomy.text.*`, `anatomy.cta_types`, `anatomy.urls`, `anatomy.image_urls`.
- URLs are token-redacted (query param `access_token` is replaced with `***REDACTED***`).

## Recipe 4: Creative previews (HTML snippets)

Goal: retrieve preview snippets for a creative.

```bash
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

Safety notes:
- Preview HTML is untrusted text. If you render it, render in a sandboxed context.

## Recipe 5: Opt-in asset downloads during snapshot export

Goal: download creative asset URLs (when present) into the pack under `assets/`.

```bash
meta-ads-api-tool --output json snapshot export \
  --ad-account-id act_<id> \
  --preset ecom_core \
  --out-dir ./exports \
  --download-assets \
  --assets-overwrite if_missing
```

Agent parsing tips:
- Look for `tables/assets.jsonl` and `manifest.assets`.
- Asset rows include per-item `status` (`downloaded`, `skipped_exists`, `failed`).
