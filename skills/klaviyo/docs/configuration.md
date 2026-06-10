# Configuration

This tool reads environment settings from `.env` (or another file with `--env-file`).

## Files

- `.env.example`: copy this file to `.env` and fill values.
- `.state/runs`: local run history, plan files, refusal summaries, and future receipt files.

## Environment variables

Required:

- `KLAVIYO_API_BASE_URL`
  - Example: `https://a.klaviyo.com`

- `KLAVIYO_API_KEY`
  - Klaviyo private API key used for live calls.

Optional:

- `KLAVIYO_COMPANY_ID`
  - Required only for `/client/*` operations.

- `KLAVIYO_API_REVISION`
  - Default: `2026-04-15`

- `KLAVIYO_TIMEOUT_S`
  - Default: `30`
