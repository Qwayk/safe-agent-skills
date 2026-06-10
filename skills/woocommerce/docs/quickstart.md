# Quickstart

This is a technical reference.
If you want the simple setup path, use [onboarding.md](onboarding.md) first.

## Smoke checks

```bash
qwayk-woocommerce-safe-agent-cli --output json --version
qwayk-woocommerce-safe-agent-cli --output json onboarding
qwayk-woocommerce-safe-agent-cli --output json auth check
qwayk-woocommerce-safe-agent-cli --output json operations list
```

## Read examples

```bash
qwayk-woocommerce-safe-agent-cli --output json products list --all --per-page 100
qwayk-woocommerce-safe-agent-cli --output json orders get --id 123
qwayk-woocommerce-safe-agent-cli --output json payment-gateways list
```

## Write examples

Dry-run plan:

```bash
qwayk-woocommerce-safe-agent-cli --output json coupons create \
  --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}' \
  --plan-out plan.json
```

Request apply after review. This currently requires explicit no-snapshot approval before WooCommerce HTTP when no saved snapshot is available:

```bash
qwayk-woocommerce-safe-agent-cli --output json --apply --plan-in plan.json \
  coupons create \
  --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}'
```

If no useful before-state can be saved, apply requires explicit no-snapshot approval before WooCommerce HTTP. Approved supported writes must create a receipt that records the recovery limit.

High-risk delete:

```bash
qwayk-woocommerce-safe-agent-cli --output json --apply --yes --plan-in delete-plan.json \
  products delete --id 123 --params-json '{"force": true}'
```
