# Command reference

Use `--env-file <path>` before the command name to choose a settings file. For a first request, use the key and command in the [quickstart](quickstart.md).

For the guided path, start with [What you can do with Sovrn](use_cases.md), [Connect your Sovrn account](onboarding.md), and [Quickstart](quickstart.md).

## Good first commands

- `sovrn-safe-cli onboarding [--no-write-env]`
- `sovrn-safe-cli --output json --version`
- `sovrn-safe-cli auth check`

`auth check` shows which settings are present. A report or link check confirms what the key can access. [API coverage](api_coverage.md) lists the requests and keys.

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

Commerce page reports cover up to 31 days per request. The start date is included and the end date is excluded. Sovrn limits the page report to one request every 60 seconds. Approved merchants returns one page at a time. Use `--page <number>` and, if needed, `--page-size <number>`. The default page size is 1,000 and the maximum is 2,500. Wait at least 10 seconds between approved-merchant requests. [Page reports](https://developer.sovrn.com/reference/get_reports-pages) · [Approved merchants](https://developer.sovrn.com/reference/post_summaries)

## Advertising reads

- `sovrn-safe-cli advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports bid get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports breakout get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue`
- `sovrn-safe-cli advertising reports domain-account get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction`
- `sovrn-safe-cli advertising reports domain-bid get --domain-name example.com --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions advertiser`
- `sovrn-safe-cli advertising reports custom get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions domain --granularity day`

You can give a publisher ID with `--publisher-id <id>` when you run an Advertising report. Use the dates and the ID for the publisher you intend to check.

## Local history

Use `runs list` or `runs show --run-id <id>` to read existing local history. To log a new report request, pass `--log-file <path>` and choose a private location.
