# Command reference

Use this page when you need the exact Skimlinks command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do with Skimlinks](use_cases.md), [Connect your Skimlinks account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

```bash
skimlinks-safe-cli onboarding
skimlinks-safe-cli onboarding --no-write-env
```

## Auth

```bash
skimlinks-safe-cli --output json --version
skimlinks-safe-cli auth check
skimlinks-safe-cli auth check --scope product
skimlinks-safe-cli auth check --scope all
```

`--scope product` uses Product Key credentials when present. If Product Key credentials are absent, the tool can fall back to shared credentials and warns that Product Key may still be disabled by Skimlinks.

## Runs

```bash
skimlinks-safe-cli runs list
skimlinks-safe-cli runs show --run-id 2026-06-08T120000Z_abc123
```

Run history is local under `.state/runs/` when a command creates run artifacts.

## Merchant API

```bash
skimlinks-safe-cli merchant merchants list [--publisher-id ID] [--publisher-domain-id ID] [--search TEXT] [--vertical ID] [--country US] [--limit N] [--offset N]
skimlinks-safe-cli merchant domains list [--publisher-id ID]
skimlinks-safe-cli merchant verticals list
skimlinks-safe-cli merchant alternative-verticals list
skimlinks-safe-cli merchant offers list [--publisher-id ID] [--search TEXT] [--merchant-id ID] [--country US] [--period TEXT] [--limit N] [--offset N]
```

Other official Merchant filters are exposed as flags: `--id`, `--favourite-type`, `--sort-by`, `--sort-dir`, `--a-id`, `--alternative-vertical-id`, `--alternative-vertical-taxonomy`, and `--alternative-vertical-country`.

## Reporting API

```bash
skimlinks-safe-cli reporting commissions search [--publisher-id ID] [--start-date DATETIME] [--end-date DATETIME] [--updated-since DATETIME]
skimlinks-safe-cli reporting aggregated get --report-by date --start-date YYYY-MM-DD --end-date YYYY-MM-DD
skimlinks-safe-cli reporting link-report query --start-date YYYY-MM-DD --end-date YYYY-MM-DD --dim device_type --met clicks
skimlinks-safe-cli reporting link-report dimensions
skimlinks-safe-cli reporting link-report metrics
skimlinks-safe-cli reporting page-report query --start-date YYYY-MM-DD --end-date YYYY-MM-DD --dim device_type --met impressions
skimlinks-safe-cli reporting page-report dimensions
skimlinks-safe-cli reporting page-report metrics
skimlinks-safe-cli reporting trending-products get --period 7_days
skimlinks-safe-cli reporting product-report get --start-date YYYY-MM-DD --end-date YYYY-MM-DD
skimlinks-safe-cli reporting payment-status get --start-date YYYY-MM-DD --end-date YYYY-MM-DD
skimlinks-safe-cli reporting deactivated-merchants get
```

Common Reporting filters include `--limit`, `--offset`, `--sort-by`, `--sort-dir`, `--currency`, `--domain-id`, `--a-id`, and report-specific filters shown in `--help`.

## Product Key

```bash
skimlinks-safe-cli product-key product get --publisher-domain-id 456 --product-url https://merchant.example/product
skimlinks-safe-cli product-key product get --publisher-domain-id 456 --upc 123456789012
skimlinks-safe-cli product-key product get --publisher-domain-id 456 --product-id B000000000 --product-id-type asin
skimlinks-safe-cli product-key product get --publisher-domain-id 456 --product-url https://merchant.example/product --sort-by epc --sort-desc desc
skimlinks-safe-cli product-key products get --publisher-domain-id 456 --product-url https://merchant.example/a --product-url https://merchant.example/b
skimlinks-safe-cli product-key products get --publisher-domain-id 456 --product-id 123456789012 --product-id 987654321098
```

Product Key requires `--publisher-domain-id` unless `SKIMLINKS_PUBLISHER_DOMAIN_ID` is set in `.env`. Product Key supports filters such as `--country-code`, `--alternative-country-code`, `--domains`, `--exclude-domains`, `--referrer-url`, `--per-merchant-limit`, `--alternatives-size`, `--sort-by`, and `--sort-desc asc|desc`. The CLI sends the official `sort_desc` string value and does not send `true` or `false`.

## Link Wrapper

```bash
skimlinks-safe-cli link-wrapper build --url https://merchant.example/product
skimlinks-safe-cli link-wrapper build --id 123X456 --url https://merchant.example/product --xcust article-1 --sref https://publisher.example/page
```

This command only builds the official `https://go.skimresources.com/` URL. It does not open the URL and does not follow redirects.
