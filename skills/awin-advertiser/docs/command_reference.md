# Command reference

Use this page when you need the exact Awin Advertiser command, flag, or write gate.
If you want the plain-English path first, start with [What you can do with Awin Advertiser](use_cases.md), [Connect your Awin advertiser account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `awin-advertiser-safe-cli onboarding [--no-write-env]`

## Auth

- `awin-advertiser-safe-cli auth check`

## Publishers

- `awin-advertiser-safe-cli publishers list --advertiser-id <id>`

## Transactions

- `awin-advertiser-safe-cli transactions list --advertiser-id <id> --start-date <ISO8601> --end-date <ISO8601> [--date-type transaction|validation|amendment] [--publisher-id <id> ...] [--status pending|approved|declined|deleted] [--timezone <value>] [--show-basket-products]`
- `awin-advertiser-safe-cli transactions by-ids --advertiser-id <id> --ids <comma-separated> [--timezone <value>] [--show-basket-products]`
- `awin-advertiser-safe-cli transactions jobs list --advertiser-id <id>`
- `awin-advertiser-safe-cli transactions jobs show --advertiser-id <id> --job-id <id> [--job-output errors|all]`
- `awin-advertiser-safe-cli transactions batch validate --advertiser-id <id> --batch-file <path> [--plan-out <path>] [--plan-in <path>] [--receipt-out <path>] [--apply --yes --ack-irreversible]`

## Offers

- `awin-advertiser-safe-cli offers create --advertiser-id <id> --offer-file <path>`

## Product feeds

- `awin-advertiser-safe-cli product-feeds upload --advertiser-id <id> --vertical retail --locale <token> --feed-file <path>`

## Reports

- `awin-advertiser-safe-cli reports publisher --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601> [--date-type transaction|validation] [--timezone <value>]`
- `awin-advertiser-safe-cli reports campaign --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601> [--campaign <value>] [--publisher-id <id> ...] [--include-numbers-without-campaign] [--interval day|month|year] [--timezone <value>]`

## Conversion

- `awin-advertiser-safe-cli conversion orders create --advertiser-id <id> --orders-file <path> [--webhook-url <url>]`

## Write gates (all write commands in this tool)

- `--apply` to apply remote changes (default is dry-run)
- `--yes` required with `--apply`
- `--ack-irreversible` required with `--apply --yes`
- `--plan-in <path>` required with `--apply`; command output plan must pass drift checks
- `--plan-out <path>` writes a dry-run plan JSON
- `--receipt-out <path>` writes a write receipt JSON
- current write families do not promise a broad saved before-state or automatic restore path

### Conversion write support

- `--apply` to apply (default is dry-run plan)
- `--yes` required with `--apply`
- `--ack-irreversible` required with `--apply --yes`
- `--plan-out <path>` to write a dry-run plan JSON
- `--plan-in <path>` required with `--apply`, and validated again on apply
- `--receipt-out <path>` to write receipt JSON after apply

## Runs

- `awin-advertiser-safe-cli runs list [--limit 20]`
- `awin-advertiser-safe-cli runs show --run-id <id>`
