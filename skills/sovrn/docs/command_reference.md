# Command reference

Use this page when you already want exact Sovrn commands.

If you want the non-technical path first, start with [What you can do](use_cases.md) and [Connect your account](onboarding.md).

## Good first commands

- `sovrn-safe-cli onboarding [--no-write-env]`
- `sovrn-safe-cli --output json --version`
- `sovrn-safe-cli auth check`

`auth check` validates local Sovrn config presence only.
Use the real `commerce` or `advertising` commands for live vendor proof.
The locked shipped surface is tracked in [API coverage](api_coverage.md).

## Commerce reads

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

## Advertising reads

- `sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports bid get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports breakout get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue`
- `sovrn-safe-cli advertising reports domain-account get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports domain-bid get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports custom get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions domain --granularity day`

## Local runs and history

The shipped Sovrn surface is read-only, so normal endpoint commands do not create run-history folders today.

The local history helpers still exist for local audit review and any future write-capable additions.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `sovrn-safe-cli runs list [--limit 20]`
- `sovrn-safe-cli runs show --run-id 2026-01-19T104512Z_a3f91c`
