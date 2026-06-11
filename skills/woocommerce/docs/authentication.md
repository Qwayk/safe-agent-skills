# Authentication

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

## Not shipped today

- HTTP-only OAuth 1.0a
- WooCommerce app authorization flow helpers

Those are official WooCommerce auth options, but they are outside this first product shape.
