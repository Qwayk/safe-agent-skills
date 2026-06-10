# Proof pack (Meta Ads tool)

Date (UTC): 2026-03-01

Last verified (UTC): 2026-03-01

Verification note:
- This repo run is **plan-only** (no live Meta credentials available here).
- Implementation is validated via offline unit tests and redacted example outputs committed under `docs/examples/outputs/`.
- To verify end-to-end, run the commands below locally with your own token.

## Offline smoke commands (no network required)

From the tool folder:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q
find . -type d -name "__pycache__" -print
meta-ads-api-tool --output json --version
meta-ads-api-tool --output json onboarding --no-write-env
```

## Offline proof artifacts (no live API)

- Unit tests (artifact-safe): `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q`
- Redacted outputs: see the files listed below in “Example outputs (redacted)”.

## Online smoke commands (requires your token)

Note: `snapshot export` writes local artifacts to `--out-dir`. Keep it outside the repo working tree.

```bash
meta-ads-api-tool --output json auth check
meta-ads-api-tool --output json ad-accounts list --fields id,name
meta-ads-api-tool --output json --ad-account-id act_<id> campaigns list --fields id,name,status --max-pages 2
meta-ads-api-tool --output json --ad-account-id act_<id> insights get --level campaign --fields campaign_id,impressions,clicks,spend --since 2026-01-01 --until 2026-01-31
meta-ads-api-tool --output json --ad-account-id act_<id> insights compare --level ad --fields ad_id,impressions,clicks,spend --since-a 2026-01-01 --until-a 2026-01-07 --since-b 2026-01-08 --until-b 2026-01-14
meta-ads-api-tool --output json snapshot export --ad-account-id act_<id> --preset maximal_firehose --out-dir /tmp/meta_ads_exports --max-pages 2
meta-ads-api-tool --output json creatives anatomy --creative-id <creative_id>
meta-ads-api-tool --output json previews get --creative-id <creative_id> --ad-format DESKTOP_FEED_STANDARD
```

## Example outputs (redacted)

- Version: `docs/examples/outputs/version.json`
- Auth check: `docs/examples/outputs/auth_check.json`
- Paginated list skeleton: `docs/examples/outputs/ad_accounts_list_paginated.json`
- Insights skeleton: `docs/examples/outputs/insights_get.json`
- Insights compare skeleton: `docs/examples/outputs/insights_compare.json`
- Presets list: `docs/examples/outputs/presets_list.json`
- Presets show: `docs/examples/outputs/presets_show.json`
- Snapshot export skeleton: `docs/examples/outputs/snapshot_export.json`
- Creatives anatomy skeleton: `docs/examples/outputs/creatives_anatomy.json`
- Previews skeleton: `docs/examples/outputs/previews_get.json`

## What can go wrong (and how we mitigate it)

- Token leaks in logs:
  - Mitigation: never print tokens; verbose HTTP logs redact `access_token` in URLs; auth uses `Authorization: Bearer`.
- Rate limits (429):
  - Mitigation: retries with backoff (configurable via `META_ADS_MAX_RETRIES`).
- Overly-large responses:
  - Mitigation: pagination controls (`--max-pages`, `--max-items`) + narrow `fields` and date ranges.
- Fieldset/permission gaps during exports:
  - Mitigation: snapshot export uses chunked multi-pass fetch + merge; default is partial-success with errors recorded in `manifest.json`; use `--strict` to fail fast.
- Local proof artifacts growth:
  - Mitigation: snapshot export writes gitignored run artifacts under `.state/runs/` (safe to delete locally).
