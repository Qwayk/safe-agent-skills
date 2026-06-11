# WooCommerce

Install slug: `woocommerce`

Use this skill when you want your AI agent to review products, orders, customers, coupons, reports, and store settings in WooCommerce with preview before live changes.

This tool gives an AI agent a safe way to use the official WooCommerce REST API v3.
It keeps reads simple, makes writes preview-first, and records either a useful before-state or a clear no-snapshot approval and recovery limit before an approved supported write proceeds.

## For non-technical users: start here

- [What you can do with this tool](docs/use_cases.md)
- [How to connect your store](docs/onboarding.md)
- [How write safety works](docs/safety_model.md)

Example requests:
- “Show me all products in this store.”
- “Preview a new coupon before creating it.”
- “List all shipping zones.”
- “Check which payment gateways are enabled.”

## For technical users: start here

- [Technical quickstart](docs/quickstart.md)
- [Command patterns](docs/command_reference.md)
- [Full endpoint coverage map](docs/api_coverage.md)

Small smoke commands:

```bash
qwayk-woocommerce-safe-agent-cli --output json --version
qwayk-woocommerce-safe-agent-cli --output json onboarding
qwayk-woocommerce-safe-agent-cli --output json --config ./qwayk.json --env-file .env onboarding
qwayk-woocommerce-safe-agent-cli --output json auth check
qwayk-woocommerce-safe-agent-cli --output json operations list
```

## Scope

- Included: the official WooCommerce REST API v3 at `/wp-json/wc/v3/`
- Not included: Store API, legacy `wc/v1` and `wc/v2`, WordPress core `/wp-json/wp/v2`, and extension-only APIs
- Auth shipped here: HTTPS REST keys, plus the official query-string fallback
