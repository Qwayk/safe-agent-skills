# Quickstart

If you’re non-technical, start with:
- `docs/use_cases.md`
- `docs/onboarding.md`

This page is a technical reference (it includes CLI commands).

This tool is **read-mostly v1**. It can read your Pinterest account data and write JSON snapshots locally. Write-capable families currently create dry-run plans or read-only previews, then require explicit no-snapshot approval before Pinterest writes when no saved snapshot is available.

## 1) Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (developer tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Copy `.env.example` → `.env` and fill your values.

Important:
- Never commit `.env` (it is gitignored).
- Never paste tokens/secrets into chat.

## 3) Authenticate

You have two options:

### Option A: 24‑hour “Generate Access Tokens” (fastest for first test)

Put the access token in `.env`:

```bash
PINTEREST_ACCESS_TOKEN=PASTE_HERE
```

This is good for quick testing, but it expires (often ~24 hours).

### Option B: Long‑term refresh-token auth (recommended)

Put these in `.env`:
- `PINTEREST_APP_ID`
- `PINTEREST_APP_SECRET`
- `PINTEREST_REFRESH_TOKEN`

If you don’t have a refresh token yet, follow `authentication.md`. The built-in auth setup helpers currently require explicit no-snapshot approval before writing local token state, so use a manually provisioned token today.

## 4) Smoke test

```bash
pinterest-api-tool auth check
```

## 5) First inventory calls

```bash
pinterest-api-tool boards list --limit 100
pinterest-api-tool pins list --limit 100
```

If you want to check board sections for a specific board:

```bash
pinterest-api-tool board-sections list --board-id BOARD_ID
pinterest-api-tool board-pins list --board-id BOARD_ID --section-id SECTION_ID
```

## 5b) Ads and catalogs (optional, read-only)

These endpoints require access to a Pinterest ad account (and may require additional scopes/tiers).

```bash
pinterest-api-tool ads accounts list
pinterest-api-tool ads campaigns list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool ads ad-groups list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool ads ads list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool ads analytics ad-account --ad-account-id AD_ACCOUNT_ID --start-date 2026-01-01 --end-date 2026-01-31 --metric IMPRESSION
pinterest-api-tool ads analytics campaigns --ad-account-id AD_ACCOUNT_ID --start-date 2026-01-01 --end-date 2026-01-31 --metric IMPRESSION

pinterest-api-tool catalogs list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool catalogs feeds list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool catalogs product-groups list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool catalogs product-group-products list --ad-account-id AD_ACCOUNT_ID --product-group-id PRODUCT_GROUP_ID
pinterest-api-tool catalogs reports list --ad-account-id AD_ACCOUNT_ID
```

## 6) Audit snapshot (writes JSON files)

```bash
pinterest-api-tool audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run
```

If analytics endpoints fail (scopes/tier), retry:

```bash
pinterest-api-tool audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --skip-analytics
```

Optional (ads/catalogs exports; warning-only on failures):

```bash
pinterest-api-tool audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --ad-account-id AD_ACCOUNT_ID --include-ads
pinterest-api-tool audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --ad-account-id AD_ACCOUNT_ID --include-catalogs
```

Notes:
- `audit snapshot` treats analytics failures as warnings, but it fails if core inventory (boards/pins) fails.
- The snapshot includes `boards_summary.json` which shows (best-effort) section counts per board.
