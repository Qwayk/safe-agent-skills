# Command reference

This page is a technical reference (it includes CLI commands).
If you’re non-technical, start with `docs/use_cases.md` and `docs/onboarding.md`.

## Onboarding

- `sovrn-safe-cli onboarding [--no-write-env]`

## Auth

- `sovrn-safe-cli --output json --version`
- `sovrn-safe-cli auth check`

Current note:
- `auth check` currently validates local Sovrn config presence only
- use the real `commerce` and `advertising` commands for live vendor calls
- the exact locked surface is tracked in `docs/api_coverage.md`

## Commerce

- `sovrn-safe-cli commerce campaigns get --search PRIMARY`
- `sovrn-safe-cli commerce links check --url https://example.com/product`
- `sovrn-safe-cli commerce links bid-check --url https://example.com/product --user-ip 203.0.113.10 --user-agent "Mozilla/5.0 ..."`
- `sovrn-safe-cli commerce reports transactions get [filters...]`
- `sovrn-safe-cli commerce reports pages get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports links get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports merchants get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports merchants-by-date get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports merchandise get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports networks get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce reports cuids get --click-date-start 2026-01-01 --click-date-end 2026-01-02 [filters...]`
- `sovrn-safe-cli commerce merchant-groups approved --campaign-id 123456`
- `sovrn-safe-cli commerce merchant-groups delta --campaign-id 123456 --since 2026-01-01T00:00:00Z`
- `sovrn-safe-cli commerce coupons product get --product-url https://merchant.example/item`
- `sovrn-safe-cli commerce products recommend --page-url article-123 --content "gift guide copy"`
- `sovrn-safe-cli commerce comparisons prices search --market usd_en --plainlink https://merchant.example/item`

## Advertising

- `sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports bid get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports breakout get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue`
- `sovrn-safe-cli advertising reports domain-account get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports domain-bid get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports custom get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions domain --granularity day`

## Runs (history)

The current official Sovrn surface in this tool is read-only. That means normal endpoint commands do not create run-history folders yet.

The local history helpers still exist because the repo standard requires them for future write-capable additions or local audit review.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `sovrn-safe-cli runs list [--limit 20]`
- `sovrn-safe-cli runs show --run-id 2026-01-19T104512Z_a3f91c`
