# Command reference

Use this page when you need the exact Awin Publisher command, flag, or write gate.
If you want the plain-English path first, start with [What you can do with Awin Publisher](use_cases.md), [Connect your Awin publisher account](onboarding.md), and [Quickstart](quickstart.md).

## Global flags

- `--env-file <path>`: env file for config (default `.env`)
- `--output json|text`: output mode
- `--timeout-s <seconds>`: request timeout override
- `--verbose`: show request logs to stderr
- `--debug`: include Python stack trace on unexpected exceptions
- `--apply`: apply the remote write command instead of dry-run
- `--yes`: extra confirmation for risky or batch writes
- `--plan-out <path>`: write a dry-run plan JSON
- `--plan-in <path>`: validate an existing plan before apply; required for `proof-of-purchase orders create` live apply
- `--receipt-out <path>`: write an apply receipt JSON after a successful apply
- `--run-id`, `--artifacts-dir`, `--no-artifacts`: run-history helpers

## Onboarding

- `awin-publisher-safe-cli onboarding`
- `awin-publisher-safe-cli onboarding --no-write-env`

## Auth

- `awin-publisher-safe-cli --output json auth check`

## Accounts

- `awin-publisher-safe-cli --output json accounts list`

## Programs

- `awin-publisher-safe-cli --output json programs list --publisher-id <publisher_id> [--relationship joined|pending|suspended|rejected|notjoined] [--country-code XX] [--include-hidden]`
- `awin-publisher-safe-cli --output json programs details --publisher-id <publisher_id> --advertiser-id <advertiser_id> [--relationship joined|pending|suspended|rejected|notjoined|any]`

## Offers

- `awin-publisher-safe-cli --output json offers list --publisher-id <publisher_id> [--advertiser-ids 1,2] [--exclusive-only] [--membership joined|notJoined|all] [--region-codes GB,US] [--status active|expiringSoon|upcoming] [--type promotion|voucher|all] [--updated-since YYYY-MM-DD] [--page N] [--page-size N]`

## Transactions

- `awin-publisher-safe-cli --output json transactions list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-02T00:00:00Z [--timezone UTC] [--date-type transaction|validation|amendment] [--advertiser-ids 1,2] [--status pending|approved|declined|deleted] [--show-basket-products]`
- `awin-publisher-safe-cli --output json transactions by-ids --publisher-id <publisher_id> --ids 100,200 [--timezone UTC] [--show-basket-products]`

## Transaction queries

- `awin-publisher-safe-cli --output json transaction-queries list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-10T00:00:00Z [--timezone UTC] [--date-type enquiryDate|transactionDate|validationDate] [--advertiser-ids 1,2] [--click-refs ref1,ref2] [--statuses pending,approved] [--page-number N] [--page-size N]`

## Reports

- `awin-publisher-safe-cli --output json reports advertiser --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB [--timezone UTC] [--date-type transaction|validation]`
- `awin-publisher-safe-cli --output json reports campaign --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB [--timezone UTC] [--date-type transaction|validation] [--advertiser-ids 1,2] [--campaign summer] [--include-numbers-without-campaign] [--interval day|month|year]`
- `awin-publisher-safe-cli --output json reports creative --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB [--timezone UTC] [--date-type transaction|validation]`

## Linkbuilder

- `awin-publisher-safe-cli --output json linkbuilder generate --publisher-id <publisher_id> --advertiser-id <advertiser_id> [--destination-url URL] [--campaign value] [--clickref value] [--clickref2 value] [--clickref3 value] [--clickref4 value] [--clickref5 value] [--clickref6 value] [--shorten]`
- `awin-publisher-safe-cli --output json linkbuilder generate-batch --publisher-id <publisher_id> --requests-file batch.json`
- `awin-publisher-safe-cli --output json linkbuilder quota --publisher-id <publisher_id>`

## Feeds

- `awin-publisher-safe-cli --output json feeds enhanced-download --publisher-id <publisher_id> --advertiser-id <advertiser_id> --locale en_GB [--vertical retail] --out enhanced-feed.jsonl [--overwrite]`
- `awin-publisher-safe-cli --output json feeds legacy-list --out legacy-feed-list.csv [--overwrite]`
- `awin-publisher-safe-cli --output json feeds legacy-download (--feed-id <feed_id> | --download-url <url>) --out legacy-feed.csv [--overwrite]`

## Proof of purchase

- `awin-publisher-safe-cli --output json --plan-out plan.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json`
- `awin-publisher-safe-cli --output json --apply --yes --plan-in plan.json [--receipt-out receipt.json] proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json`
- Official live use is also gated by Awin-side publisher enablement and advertiser-side CLO enablement.

## Run history

- `awin-publisher-safe-cli runs list [--limit 20]`
- `awin-publisher-safe-cli runs show --run-id <id>`
