# Authentication

WooCommerce authentication is meant to be local and checked before an agent works with products, orders, customers, coupons, reports, and store settings. Keep the store URL, consumer key, and consumer secret in `.env`, and do not paste them into chat.

The shipped path uses WooCommerce REST API credentials. The safe check should prove those credentials work without printing the secret values or changing the store.

A good first auth check is: "Confirm the WooCommerce store URL, consumer key, and consumer secret are configured, run the safe auth check, and tell me whether the store is reachable without showing secrets."

## Shipped auth path

This version ships the simplest official auth path that reaches the WooCommerce REST API v3 surface:

- HTTPS store URL
- WooCommerce REST API consumer key and consumer secret
- HTTP Basic Auth by default

## Fallback

If the store or proxy strips the `Authorization` header, set:

```dotenv
WOOCOMMERCE_QUERY_STRING_AUTH=true
```

The tool will then use the official `consumer_key` and `consumer_secret` query-string fallback.

## Not shipped in this version

- HTTP-only OAuth 1.0a
- WooCommerce app authorization flow helpers

Those are official WooCommerce auth options, but they are outside this first product shape.
