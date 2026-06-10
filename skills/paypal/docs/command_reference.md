# Command reference

Use this page when you need the exact PayPal command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Public local commands

- `qwayk-paypal-safe-agent-cli --output json --version`
- `qwayk-paypal-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-paypal-safe-agent-cli auth check`
- `qwayk-paypal-safe-agent-cli runs list [--limit 20]`
- `qwayk-paypal-safe-agent-cli runs show --run-id <run_id>`

## Global flags

- `--env-file <path>`: choose a local `.env` file
- `--timeout-s <seconds>`: override request timeout
- `--output json|text`: default is `json`
- `--verbose`: print HTTP start and end lines to stderr
- `--debug`: show Python stack traces
- `--log-file <path>`: optional global JSONL audit log
- `--apply`: execute a write instead of returning a dry-run plan
- `--yes`: extra confirmation for higher-risk actions when the command requires it, including some deletes and some non-delete state changes
- `--ack-irreversible`: currently unused by the shipped PayPal command surface; reserved for future commands if the runtime later adds one
- `--plan-out <path>`: save the dry-run plan JSON
- `--plan-in <path>`: no shipped PayPal command currently requires this; kept for future high-risk apply flows
- `--receipt-out <path>`: writes an approved apply receipt when the supported write proceeds; missing approval or failed safety checks do not create it
- `--run-id <id>`: set the run id explicitly
- `--artifacts-dir <path>`: override the run-artifact folder
- `--no-artifacts`: disable local run artifacts

## API family commands

The shipped PayPal API surface is grouped into 17 families and 133 explicit commands:

- `catalog-products` (4)
- `disputes` (15)
- `identity-v1` (1)
- `identity-v2` (5)
- `invoicing` (27)
- `orders` (8)
- `partner-referrals` (2)
- `payment-experience` (6)
- `payment-tokens` (6)
- `payments` (8)
- `payouts` (4)
- `pricing` (1)
- `referenced-payouts` (4)
- `subscriptions` (17)
- `tracking` (5)
- `transaction-search` (4)
- `webhooks` (16)

Use `api_coverage.md` when you need the exact command for a specific PayPal endpoint.

## Naming rules

- Commands use `family action`.
- Path placeholders become CLI flags like `--id`, `--invoice-id`, and `--webhook-id`.
- JSON request bodies use `--body-file <path>`.
- Some PayPal namespaces stay close to the official docs, so a few action names include dots, such as `payments authorizations.get` and `webhooks webhooks-lookup.post`.

## Read pattern

```bash
qwayk-paypal-safe-agent-cli <family> <action> [flags]
```

Examples:

- `qwayk-paypal-safe-agent-cli orders get --id ORDER-ID`
- `qwayk-paypal-safe-agent-cli payments authorizations.get --authorization-id AUTH-ID`
- `qwayk-paypal-safe-agent-cli webhooks list`

Read operations run directly.

## Write pattern

Dry-run first:

```bash
qwayk-paypal-safe-agent-cli --output json <family> <action> [path flags] --body-file body.json --plan-out plan.json
```

Apply request after review:

```bash
qwayk-paypal-safe-agent-cli --output json --apply <family> <action> [path flags] --body-file body.json --receipt-out receipt.json
```

When command-specific saved snapshot support is not available, write apply requires explicit no-snapshot approval before PayPal auth or HTTP. Approved supported writes create receipts; missing approval or failed safety checks do not.

Write plans include `before_state` and a no-recovery contract:

- `recovery.automatic_rollback: false`
- `recovery.snapshots: []`
- `recovery.backups: []`
- `recovery.rollback_plan: null`

Some higher-risk actions also need `--yes`:

```bash
qwayk-paypal-safe-agent-cli --output json --apply --yes payment-tokens delete --id PAYTOK-ID
qwayk-paypal-safe-agent-cli --output json --apply --yes disputes accept-claim --id DISP-ID
qwayk-paypal-safe-agent-cli --output json --apply --yes payments authorizations.void --authorization-id AUTH-ID
```

## Read-like `POST` commands

Some PayPal endpoints use `POST` even though they are query or verification style operations.
These stay read-only in this tool and do not require `--apply`:

- `invoicing search-invoices`
- `invoicing invoices-generate-next-invoice-number`
- `invoicing invoices-generate-qr-code`
- `payments find-eligible-methods`
- `pricing quote-exchange-rates`
- `webhooks verify-webhook-signature`
