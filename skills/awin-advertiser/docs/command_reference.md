# Command reference

Run these commands from the installed environment. Put global flags such as `--env-file <path>` before the command name. Use the same settings file for setup, preview, and apply.

[First report](quickstart.md) · [Setup and connection help](onboarding.md) · [Approval and receipt guide](safety_model.md)

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

## Preview, approve and check a change

- Run the write command with `--plan-out <path>` to save its preview.
- After approval, use the same input and pass `--apply --yes --ack-irreversible --plan-in <path>`. The write flags go before the command name or after the final subcommand.
- Add `--receipt-out <path>` to choose where to save the receipt. By default, the CLI saves it with that run. `--no-artifacts` disables the default run files.
- If the plan is refused, compare the account, settings and input, then make a new plan. For a rejected batch, check the action and its transaction fields against [Awin's batch examples](https://help.awin.com/apidocs/approve-decline-amend-batch-transactions-for-a-given-advertiser).
- If Awin accepted a request for later processing, returns only some results, or the reply was lost, check Awin before resending. Read `result.state` and the receipt's `verification` together. An accepted request can return `ok: true` while verification is still pending.

## Runs

- `awin-advertiser-safe-cli runs list [--limit 20]`
- `awin-advertiser-safe-cli runs show --run-id <id>`
