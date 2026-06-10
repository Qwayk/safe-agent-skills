---
name: awin-advertiser-safe-cli
description: Awin advertiser safe CLI for read checks and advertiser write flows.
commands:
  - awin-advertiser-safe-cli onboarding
  - awin-advertiser-safe-cli auth check
  - awin-advertiser-safe-cli publishers list --advertiser-id <id>
  - awin-advertiser-safe-cli transactions list --advertiser-id <id> --start-date <ISO8601> --end-date <ISO8601>
  - awin-advertiser-safe-cli transactions by-ids --advertiser-id <id> --ids <comma-separated>
  - awin-advertiser-safe-cli transactions jobs list --advertiser-id <id>
  - awin-advertiser-safe-cli transactions jobs show --advertiser-id <id> --job-id <id> [--job-output errors|all]
  - awin-advertiser-safe-cli transactions batch validate --advertiser-id <id> --batch-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]
  - awin-advertiser-safe-cli reports publisher --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601>
  - awin-advertiser-safe-cli reports campaign --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601>
  - awin-advertiser-safe-cli offers create --advertiser-id <id> --offer-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]
  - awin-advertiser-safe-cli product-feeds upload --advertiser-id <id> --vertical retail --locale <token> --feed-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]
  - awin-advertiser-safe-cli conversion orders create --advertiser-id <id> --orders-file <path> [--webhook-url <url>] [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]
  - awin-advertiser-safe-cli runs list
  - awin-advertiser-safe-cli runs show
---

Use this skill only with these commands:
- `awin-advertiser-safe-cli onboarding [--no-write-env]`
- `awin-advertiser-safe-cli auth check`
- `awin-advertiser-safe-cli publishers list --advertiser-id <id>`
- `awin-advertiser-safe-cli transactions list --advertiser-id <id> --start-date <ISO8601> --end-date <ISO8601>`
- `awin-advertiser-safe-cli transactions by-ids --advertiser-id <id> --ids <comma-separated>`
- `awin-advertiser-safe-cli transactions jobs list --advertiser-id <id>`
- `awin-advertiser-safe-cli transactions jobs show --advertiser-id <id> --job-id <id> [--job-output errors|all]`
- `awin-advertiser-safe-cli transactions batch validate --advertiser-id <id> --batch-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]`
- `awin-advertiser-safe-cli reports publisher --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601> [--date-type transaction|validation] [--timezone <value>]`
- `awin-advertiser-safe-cli reports campaign --advertiser-id <id> --start-date <YYYY-MM-DD or ISO8601> --end-date <YYYY-MM-DD or ISO8601> [--campaign <value>] [--publisher-id <id> ...] [--include-numbers-without-campaign] [--interval day|month|year] [--timezone <value>]`
- `awin-advertiser-safe-cli offers create --advertiser-id <id> --offer-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]`
- `awin-advertiser-safe-cli product-feeds upload --advertiser-id <id> --vertical retail --locale <token> --feed-file <path> [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]`
- `awin-advertiser-safe-cli conversion orders create --advertiser-id <id> --orders-file <path> [--webhook-url <url>] [--apply --yes --ack-irreversible --plan-in <path>] [--plan-out <path>] [--receipt-out <path>]`
- `awin-advertiser-safe-cli runs list [--limit N]`
- `awin-advertiser-safe-cli runs show --run-id <id>`

Rules:
- Always call with `--output json`.
- Never output `.env` content or token values.
- Never expose Authorization headers or raw order data.
- If the user asks for a command not in this list, reply: `No such live command in this slice.`
