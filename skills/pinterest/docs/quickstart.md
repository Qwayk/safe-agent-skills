# Quickstart

Want the short non-technical path first? Start with [What you can do with Pinterest](use_cases.md), [Connect your Pinterest account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

This tool is read-mostly today. It can read Pinterest account data and write JSON snapshots locally. Remote write families stay plan-first and still need explicit no-snapshot approval before live Pinterest changes.

## 1) Install

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (developer tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Copy `.env.example` to `.env`, then fill your values from [Configuration](configuration.md).

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

If you do not have a refresh token yet, follow [Authentication details](authentication.md). The built-in auth setup helpers still require explicit no-snapshot approval before writing local token state, so the safest first path is a manually provisioned token.

## 4) First safe checks

```bash
pinterest-api-tool --output json --version
pinterest-api-tool --output json auth check
pinterest-api-tool --output json boards list --limit 1
```

## 5) Common inventory commands

```bash
pinterest-api-tool --output json boards list --limit 100
pinterest-api-tool --output json pins list --limit 100
```

If you want to check board sections for a specific board:

```bash
pinterest-api-tool --output json board-sections list --board-id BOARD_ID
pinterest-api-tool --output json board-pins list --board-id BOARD_ID --section-id SECTION_ID
```

## 6) Ads and catalogs reads

These endpoints require access to a Pinterest ad account (and may require additional scopes/tiers).

```bash
pinterest-api-tool --output json ads accounts list
pinterest-api-tool --output json ads campaigns list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json ads ad-groups list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json ads ads list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json ads analytics ad-account --ad-account-id AD_ACCOUNT_ID --start-date 2026-01-01 --end-date 2026-01-31 --metric IMPRESSION
pinterest-api-tool --output json ads analytics campaigns --ad-account-id AD_ACCOUNT_ID --start-date 2026-01-01 --end-date 2026-01-31 --metric IMPRESSION

pinterest-api-tool --output json catalogs list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json catalogs feeds list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json catalogs product-groups list --ad-account-id AD_ACCOUNT_ID
pinterest-api-tool --output json catalogs product-group-products list --ad-account-id AD_ACCOUNT_ID --product-group-id PRODUCT_GROUP_ID
pinterest-api-tool --output json catalogs reports list --ad-account-id AD_ACCOUNT_ID
```

## 7) Audit snapshot

```bash
pinterest-api-tool --output json audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run
```

If analytics endpoints fail (scopes/tier), retry:

```bash
pinterest-api-tool --output json audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --skip-analytics
```

Optional (ads/catalogs exports; warning-only on failures):

```bash
pinterest-api-tool --output json audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --ad-account-id AD_ACCOUNT_ID --include-ads
pinterest-api-tool --output json audit snapshot --out-dir <PROJECT_DIR>/pinterest/audits/first-run --ad-account-id AD_ACCOUNT_ID --include-catalogs
```

Notes:
- `audit snapshot` treats analytics failures as warnings, but it fails if core inventory (boards/pins) fails.
- The snapshot includes `boards_summary.json` which shows (best-effort) section counts per board.

## 8) Write planning rules

If you move from reads into live Pinterest changes:

- start with the dry-run plan first
- use `--apply --yes` for confirmed write attempts
- add `--ack-irreversible`, `--ack-spend`, or `--ack-volume` when the command requires them
- expect `--ack-no-snapshot` too when the write has no saved before-state
