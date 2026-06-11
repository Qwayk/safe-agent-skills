# Command reference

Use this page when you need the exact WooCommerce command, flag, or safety rule.
If you want the plain-English path first, start with [What you can do](use_cases.md), [Connect your account](onboarding.md), and [Quickstart](quickstart.md).

## Local commands

- `qwayk-woocommerce-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-woocommerce-safe-agent-cli auth check`
- `qwayk-woocommerce-safe-agent-cli operations list`
- `qwayk-woocommerce-safe-agent-cli runs list [--limit 20]`
- `qwayk-woocommerce-safe-agent-cli runs show --run-id <run_id>`

Global flags:

- `--version`: Print the tool version and exit.
- `--config <path>`: JSON defaults file for non-secret values.
- `--env-file <path>`: Path to `.env` file.
- `--timeout-s <float>`: Override request timeout (CLI flags win over config).
- `--output json|text`: Select output mode.
- `--verbose`: Turn on HTTP debug logs to stderr.
- `--debug`: Show stack traces on errors.
- `--log-file <path>`: Optional global JSONL audit log.
- `--apply`: Request apply after review. Current writes require explicit no-snapshot approval before WooCommerce HTTP when no saved snapshot is available.
- `--yes`: Extra confirmation for high-risk writes.
- `--plan-out <path>`: Write dry-run plan JSON to a file.
- `--plan-in <path>`: Apply from a reviewed plan file.
- `--receipt-out <path>`: Write an approved apply receipt JSON to a file.
- `--run-id <id>`: Optional run id for local history.
- `--artifacts-dir <path>`: Optional custom artifacts directory.
- `--no-artifacts`: Disable run artifacts and run history writing.

## Read pattern

```bash
qwayk-woocommerce-safe-agent-cli --output json <family> <action> [path flags] [--params-file <path> | --params-json '{"key":"value"}']
```

List commands that support pagination also accept:

- `--page`
- `--per-page`
- `--all`
- `--max-pages`

## Write pattern

Dry-run first:

```bash
qwayk-woocommerce-safe-agent-cli --output json <family> <action> [path flags] [--body-file <path> | --body-json '{...}'] --plan-out plan.json
```

Request apply after review. This requires explicit no-snapshot approval before WooCommerce HTTP when the operation cannot save real before-state:

```bash
qwayk-woocommerce-safe-agent-cli --output json --apply --ack-no-snapshot --plan-in plan.json <family> <action> [path flags] [--body-file <path> | --body-json '{...}']
```

High-risk write apply requests also need `--yes`.

The tool does not create WooCommerce snapshots, provider backups, or machine rollback plans.
Approved supported write apply creates a receipt that records the no-snapshot approval and recovery limit. Missing approval or failed safety checks create refusal output instead.

Use either one params flag and one body flag per command:

- `--params-file` or `--params-json`
- `--body-file` or `--body-json`

## Main command families

- `index`
- `coupons`, `customers`, `orders`, `order-actions`, `order-notes`, `order-refunds`, `refunds`
- `products`, `product-variations`, `product-attributes`, `product-attribute-terms`, `product-categories`, `product-custom-fields`, `product-shipping-classes`, `product-tags`, `product-reviews`
- `reports`, `taxes`, `tax-classes`, `webhooks`
- `settings`, `setting-options`, `payment-gateways`
- `shipping-zones`, `shipping-zone-locations`, `shipping-zone-methods`, `shipping-methods`
- `system-status`, `system-status-tools`, `data`
