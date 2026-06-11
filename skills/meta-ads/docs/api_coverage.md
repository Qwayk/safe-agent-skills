# API coverage (Meta Ads / Marketing API)

Last audited (UTC): 2026-03-01

Provider: Meta (Marketing API / Graph API)
Default base URL: `https://graph.facebook.com`
Default API version: `v24.0` (see `src/meta_ads_api_tool/config.py`)

This is a **read-only** tool: GET-only.

## Coverage ledger (Graph paths/edges → CLI)

### Auth

- `GET /vXX.X/me` → `auth check` (me mode; fallback when no ad account id is known)
- `GET /vXX.X/act_{ad_account_id}` → `auth check` (ad_account mode) and `ad-accounts get`

### Presets (local)

- Local (no API calls) → `presets list`, `presets show`

### Snapshot export (analysis pack)

`snapshot export` is a batched GET-only workflow that calls multiple edges and writes a local pack:

- `GET /vXX.X/act_{ad_account_id}/campaigns` → `snapshot export` (campaigns table)
- `GET /vXX.X/act_{ad_account_id}/adsets` → `snapshot export` (ad_sets table)
- `GET /vXX.X/act_{ad_account_id}/ads` → `snapshot export` (ads table)
- `GET /vXX.X/act_{ad_account_id}/adcreatives` → `snapshot export` (creatives table)
- `GET /vXX.X/act_{ad_account_id}/insights` → `snapshot export` (insights table)
- Local (no additional API calls):
  - Derived from `adcreatives` payloads → `snapshot export` (`creative_anatomy` + `asset_urls` tables)
- Optional local downloads (opt-in):
  - `GET https://...` (asset URLs found in creative payloads) → `snapshot export --download-assets` (assets folder + assets table)

Implementation notes:
- Fields may be fetched in **chunks** and merged locally (partial-success by default; `--strict` to fail on any chunk error).
- Paging URLs are redacted before being returned in stdout JSON (tokens never emitted).
- Snapshot insights can be time-bounded via `--since/--until` or `--date-preset` (both override preset/`--param`).
- Extra insights breakdown tables can be added via `--extra-insights-breakdown-table suffix:breakdowns_csv` (repeatable).

### Ad accounts

- `GET /vXX.X/me/adaccounts` → `ad-accounts list`
- `GET /vXX.X/act_{ad_account_id}` → `ad-accounts get`

### Campaigns / ad sets / ads

- `GET /vXX.X/act_{ad_account_id}/campaigns` → `campaigns list`
- `GET /vXX.X/{campaign_id}` → `campaigns get`

- `GET /vXX.X/act_{ad_account_id}/adsets` → `ad-sets list`
- `GET /vXX.X/{adset_id}` → `ad-sets get`

- `GET /vXX.X/act_{ad_account_id}/ads` → `ads list`
- `GET /vXX.X/{ad_id}` → `ads get`

### Creatives / images / videos

- `GET /vXX.X/act_{ad_account_id}/adcreatives` → `creatives list`
- `GET /vXX.X/{creative_id}` → `creatives get`
- Local (no API calls beyond `creatives get`) → `creatives anatomy` (normalized creative anatomy + extracted asset URLs)

- `GET /vXX.X/act_{ad_account_id}/adimages` → `images list`
- `GET /vXX.X/{image_id}` → `images get`

- `GET /vXX.X/act_{ad_account_id}/advideos` → `videos list`
- `GET /vXX.X/{video_id}` → `videos get`

### Insights

- `GET /vXX.X/act_{ad_account_id}/insights` → `insights get`
- `GET /vXX.X/act_{ad_account_id}/insights` (two calls) → `insights compare`
  - Supported query patterns:
    - `level={account|campaign|adset|ad}`
    - `fields=...`
    - `time_range={"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}` (JSON-encoded)
    - `breakdowns=a,b,c`
    - `time_increment=...`
    - `action_breakdowns=...`
    - `action_attribution_windows=...`
    - Additional params via `--param k=v`

### Previews

- `GET /vXX.X/{creative_id}/previews` → `previews get`

## Not implemented (intentionally)

- Any non-GET endpoint (create/update/delete/pause/budget changes, async report creation via POST, uploads).
- Any “apply/yes” remote-write flow or receipts (this phase is read-only).
