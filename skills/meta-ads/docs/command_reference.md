# Command reference

Use this page when you need the exact Meta Ads command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `meta-ads-api-tool onboarding [--no-write-env]`

## Auth

- `meta-ads-api-tool auth check`

## Presets

- List:
  - `meta-ads-api-tool presets list`

- Show:
  - `meta-ads-api-tool presets show --preset <id>`

## Snapshot export

- Export (manifest + JSONL tables):
  - `meta-ads-api-tool snapshot export --ad-account-id <id|act_id> --preset <id> --out-dir <dir> [--run-id <id>] [--strict] [--download-assets --assets-overwrite never|if_missing|always] [--limit N] [--fields-chunk-size N] [--param k=v ...] [--max-pages N] [--max-items N]`
  - Snapshot insights controls (optional; override preset/--param):
    - `--since YYYY-MM-DD --until YYYY-MM-DD` (time_range)
    - `--date-preset <name>` (example: `last_7d`, `last_28d`)
    - `--insights-time-increment <val>`
    - `--insights-breakdown <name> ...`
    - `--insights-action-breakdown <val> ...`
    - `--insights-action-attribution-window <val> ...`
    - `--extra-insights-breakdown-table <suffix:breakdowns_csv> ...` (example: `placement:publisher_platform,platform_position`)
  - Snapshot fields overrides (optional):
    - `--fields-campaigns ...`
    - `--fields-ad-sets ...`
    - `--fields-ads ...`
    - `--fields-creatives ...`
    - `--fields-insights ...`

## Ad accounts

- List:
  - `meta-ads-api-tool ad-accounts list [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool ad-accounts get --ad-account-id <id|act_id> [--fields ...] [--param k=v ...]`

## Campaigns

- List:
  - `meta-ads-api-tool campaigns list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool campaigns get --campaign-id <id> [--fields ...] [--param k=v ...]`

## Ad sets

- List:
  - `meta-ads-api-tool ad-sets list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool ad-sets get --ad-set-id <id> [--fields ...] [--param k=v ...]`

## Ads

- List:
  - `meta-ads-api-tool ads list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool ads get --ad-id <id> [--fields ...] [--param k=v ...]`

## Creatives

- List:
  - `meta-ads-api-tool creatives list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool creatives get --creative-id <id> [--fields ...] [--param k=v ...]`

- Anatomy:
  - `meta-ads-api-tool creatives anatomy --creative-id <id> [--fields ...] [--param k=v ...]`

## Previews

- Get creative previews:
  - `meta-ads-api-tool previews get --creative-id <id> [--ad-format <name>] [--param k=v ...]`

## Images

- List:
  - `meta-ads-api-tool images list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool images get --image-id <id> [--fields ...] [--param k=v ...]`

## Videos

- List:
  - `meta-ads-api-tool videos list --ad-account-id <id|act_id> [--fields ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Get:
  - `meta-ads-api-tool videos get --video-id <id> [--fields ...] [--param k=v ...]`

## Insights

- Get:
  - `meta-ads-api-tool insights get --ad-account-id <id|act_id> --level {account,campaign,adset,ad} [--fields ...] [--since YYYY-MM-DD --until YYYY-MM-DD] [--breakdown <name> ...] [--time-increment <val>] [--action-breakdown <val> ...] [--action-attribution-window <val> ...] [--param k=v ...] [--max-pages N] [--max-items N]`

- Compare two ranges:
  - `meta-ads-api-tool insights compare --ad-account-id <id|act_id> --level {account,campaign,adset,ad} [--fields ...] --since-a YYYY-MM-DD --until-a YYYY-MM-DD --since-b YYYY-MM-DD --until-b YYYY-MM-DD [--breakdown <name> ...] [--time-increment <val>] [--action-breakdown <val> ...] [--action-attribution-window <val> ...] [--param k=v ...] [--max-pages N] [--max-items N]`
