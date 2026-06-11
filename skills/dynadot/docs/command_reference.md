# Command reference

Use this page when you need the exact Dynadot command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Onboarding

- `dynadot-api-tool onboarding [--no-write-env]`

## Auth

- `dynadot-api-tool --output json --version`
- `dynadot-api-tool auth check`

## API3 (all official commands; read + write)

This tool implements **every official Dynadot API3** `command=` value via first-class subcommands under `api3/`.

Discovery:
- `dynadot-api-tool api3 --help`
- `dynadot-api-tool api3 <command> --help`

Examples (preview-only; no live write):
- `dynadot-api-tool --output json api3 register --domain example.com --duration 1 --currency USD`
- `dynadot-api-tool --output json --plan-out plan.json api3 set-privacy --domain example.com --option off --whois-privacy-option yes`
- `dynadot-api-tool --output json --plan-out plan.json api3 place-auction-bid --domain example.com --bid-amount 100 --currency usd`

Apply (requires reviewed plan + confirmations):
- `dynadot-api-tool --output json --apply --yes --plan-in plan.json api3 set-privacy --domain example.com --option off --whois-privacy-option yes`

Write contract:
- Dynadot write plans are currently `irreversible_and_clearly_labeled`.
- Every write plan includes `before_state` with `status: no_snapshot_available`.
- Apply attempts run the normal gates, then require explicit no-snapshot approval before Dynadot HTTP when command-specific saved snapshot support is not available.
- Approved supported writes create receipts; missing approval or failed safety checks do not.
- Every write plan includes `recovery`.
- `recovery.end_state` is `irreversible_and_clearly_labeled`.
- `recovery.backups = []`, `recovery.snapshots = []`, and `recovery.rollback_plan = null`.
- Any read-back plans are verification notes only. They are not restoreable backups.

## Account (read-only)

- `dynadot-api-tool account info [--out export.json]`
- `dynadot-api-tool account balance [--out export.json]`
- `dynadot-api-tool account coupons --coupon-type {registration,renewal,transfer} [--out export.json]`

## Pricing (read-only)

- `dynadot-api-tool pricing tld-price [--currency {USD,EUR,CNY}] [--page N] [--page-size N] [--out export.json]`

## Marketplace (read-only)

- `dynadot-api-tool marketplace listings list [--currency {USD,EUR,CNY}] [--exclude-pending-sale] [--show-other-registrar] [--page N] [--page-size N] [--out export.json]`
- `dynadot-api-tool marketplace listings get --domain example.com [--currency {USD,EUR,CNY}] [--out export.json]`

## Auctions (read-only)

- `dynadot-api-tool auctions open [--currency {USD,EUR,CNY}] [--page N] [--page-size N] [--type TYPE ...] [--out export.json]`
- `dynadot-api-tool auctions closed --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--currency {USD,EUR,CNY}] [--out export.json]`
- `dynadot-api-tool auctions details --domain example.com [--domain other.com ...] [--currency {USD,EUR,CNY}] [--out export.json]`
- `dynadot-api-tool auctions bids [--currency {USD,EUR,CNY}] [--page N] [--page-size N] [--out export.json]`

## Backorder auctions (read-only)

- `dynadot-api-tool backorder-auctions closed --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--currency {USD,EUR,CNY}] [--out export.json]`
- `dynadot-api-tool backorder-auctions details --domain example.com [--currency {USD,EUR,CNY}] [--out export.json]`

## Closeouts (read-only)

- `dynadot-api-tool closeouts list [--domain example.com] [--currency {USD,EUR,CNY}] [--page N] [--page-size N] [--out export.json]`

## Backorders (read-only)

- `dynadot-api-tool backorders requests list --start-date YYYY-MM-DD --end-date YYYY-MM-DD [--out export.json]`

## CN audit (read-only)

- `dynadot-api-tool cn-audit status --contact-id 12345 [--gtld] [--out export.json]`

## Transfers (read-only)

- `dynadot-api-tool transfers list [--out export.json]`
- `dynadot-api-tool transfers status --domain example.com --transfer-type {in,away} [--out export.json]`
- `dynadot-api-tool transfers auth-code --domain example.com [--out export.json]`
  - Treat the returned auth/EPP code as sensitive (don’t paste it into tickets or public chat).

## Orders (read-only)

- `dynadot-api-tool orders list --search-by {date_range,domain,order_id} --start-date yyyy/MM/dd --end-date yyyy/MM/dd [--payment-method "account_balance,credit_card"] [--out export.json]`
- `dynadot-api-tool orders status --order-id 123456 [--out export.json]`

## Contacts (read-only)

- `dynadot-api-tool contacts list [--out export.json]`
- `dynadot-api-tool contacts get --contact-id 123 [--out export.json]`

## DNS (read-only)

- `dynadot-api-tool dns get --domain example.com [--out export.json]`

## Domains (push workflows)

Sender side:
- `dynadot-api-tool domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>" [--max-batches N] [--sleep-between-batches-s S] [--resume-from-receipt receipt.json]`
- `dynadot-api-tool --apply --yes --plan-in plan.json domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>" [--max-batches N] [--sleep-between-batches-s S] [--resume-from-receipt receipt.json]`

Receiver side:
- `dynadot-api-tool domains push-requests list`
- `dynadot-api-tool --apply --yes --plan-in plan.json domains push-requests accept --domains-file "<FILE>" [--max-batches N] [--sleep-between-batches-s S] [--resume-from-receipt receipt.json]`
- `dynadot-api-tool --apply --yes --plan-in plan.json domains push-requests decline --domains-file "<FILE>" [--max-batches N] [--sleep-between-batches-s S] [--resume-from-receipt receipt.json]`

Apply result:
- These write commands require reviewed `--plan-in`, `--yes`, and explicit no-snapshot approval when no saved before-state exists. Receipts record which approved writes ran and what recovery is possible.

## Transfer (guided end-to-end)

This is the “one workflow” command. It runs:
push (sender) → accept (receiver) → confirm domains are present → check/fix name servers → summary.

Notes:
- You run it using the **sender** account as the main `--env-file`.
- You pass the **receiver** account using `--receiver-env-file`.
- It only selects domains whose Dynadot status is `active`.
- Presence checks are done with per-domain `domain_info` calls (accurate for large accounts; can be slower). You can slow it down with `--presence-domain-info-sleep-s`.
- If you hit Dynadot rate limits on large runs, slow down:
  - `--sender-status-sleep-s` (sender eligibility checks)
  - `--presence-domain-info-sleep-s` (receiver presence checks)
  - `--ns-sleep-between-verifications-s` (receiver get_ns pacing)

Preview (plan):
- `dynadot-api-tool --output json --plan-out plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"`

Apply (requires `--apply --yes` and reviewed `--plan-in`):
- `dynadot-api-tool --output json --apply --yes --plan-in plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"`

Apply result:
- `transfer run` requires explicit no-snapshot approval before sender or receiver Dynadot HTTP when sender or receiver before-state cannot be saved.

Safe resume:
- `dynadot-api-tool --output json --plan-out plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net" --resume-from-receipt receipt.json`

## Domains (name servers: audit + bulk set)

Audit/export current name servers:
- `dynadot-api-tool domains name-servers export --domains-file "<FILE>" [--sleep-s S] [--max-domains N] [--out export.json]`
- `dynadot-api-tool domains name-servers export --domains-export-in domains.list.json [--sleep-s S] [--max-domains N] [--out export.json]`

Tip: to generate `domains.list.json`:
- `dynadot-api-tool domains list --all --out domains.list.json`

Diff vs desired name servers:
- `dynadot-api-tool domains name-servers diff --current-in export.json --desired-ns "ns1.example.net" --desired-ns "ns2.example.net" [--out diff.json]`
- `dynadot-api-tool domains name-servers diff --current-in export.json --desired-ns-file desired_ns.txt [--out diff.json]`

Set name servers (preview first, then apply):
- `dynadot-api-tool --plan-out plan.json domains name-servers set --diff-in diff.json [--max-domains N] [--max-batches N] [--sleep-between-batches-s S] [--sleep-between-verifications-s S] [--continue-on-error] [--resume-from-receipt receipt.json] [--skip-availability-check] [--require-available-name-servers]`
- `dynadot-api-tool --apply --yes --plan-in plan.json domains name-servers set --diff-in diff.json [--max-domains N] [--max-batches N] [--sleep-between-batches-s S] [--sleep-between-verifications-s S] [--continue-on-error] [--resume-from-receipt receipt.json] [--skip-availability-check] [--require-available-name-servers]`

Important:
- The default availability check is only a warning based on Dynadot `server_list`.
- For external providers like Cloudflare, missing entries in `server_list` can still work.
- Apply requires explicit no-snapshot approval before the availability check or `set_ns` call when per-domain before-state cannot be saved.
- Use `--require-available-name-servers` only when you intentionally want Dynadot `server_list` to be a hard blocker.

## Domains (inventory exports, read-only)

- `dynadot-api-tool domains list [--page N] [--page-size N] [--all] [--max-pages N] [--sleep-s S] [--out export.json]`
- `dynadot-api-tool domains info [--domain example.com] [--domains-file domains.txt] [--sleep-s S] [--max-domains N] [--out export.json]`
- `dynadot-api-tool domains status [--domain example.com] [--domains-file domains.txt] [--sleep-s S] [--max-domains N] [--out export.json]`
- `dynadot-api-tool domains folders list [--out export.json]`
- `dynadot-api-tool domains search --domain example.com [--domain other.com ...] [--show-price] [--currency {USD,EUR,CNY}] [--out export.json]`

## Jobs

- `dynadot-api-tool jobs run --file jobs.csv [--limit N] [--plan-out plan.json]`
- `dynadot-api-tool --apply --yes --plan-in plan.json jobs run --file jobs.csv`

## Runs (history)

Write-capable commands automatically save proof artifacts under `.state/runs/` and append an index row to `.state/runs/index.jsonl`.

These live next to your `--env-file` (usually next to your `.env` file), so they’re easy to find.

Optional flags:
- `--run-id <id>`: set a specific run id (otherwise the tool generates one)
- `--artifacts-dir <path>`: override where artifacts are written for this run
- `--no-artifacts`: disable writing run artifacts (advanced)

- `dynadot-api-tool runs list [--limit 20]`
- `dynadot-api-tool runs show --run-id 2026-01-19T104512Z_a3f91c`

## Demo (plan/receipt workflow examples)

- `dynadot-api-tool demo read`
- `dynadot-api-tool demo write --selector demo-resource [--plan-out plan.json]`
- `dynadot-api-tool --apply --yes --plan-in plan.json --receipt-out receipt.json demo write --selector demo-resource`

Review note:
- For any write family above, read the plan `before_state` and `recovery` blocks as the real safety contract.
