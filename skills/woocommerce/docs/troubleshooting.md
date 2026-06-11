# Troubleshooting

## `Missing WOOCOMMERCE_STORE_URL`

Add your store home URL to `.env`.

## `Missing WOOCOMMERCE_CONSUMER_KEY or WOOCOMMERCE_CONSUMER_SECRET`

Create a WooCommerce REST API key in `WooCommerce > Settings > Advanced > REST API` and paste both values into `.env`.

## `401` or `consumer_key` errors

Try `WOOCOMMERCE_QUERY_STRING_AUTH=true`.
Some hosts or proxies strip the `Authorization` header.

## SSL problems on a local test store

Use `WOOCOMMERCE_VERIFY_SSL=false` only for local self-signed test stores.

## A write command refuses to apply

That is expected if you did not pass `--apply --plan-in`.
High-risk writes also need `--yes`.
After those gates pass, current write apply still requires explicit no-snapshot approval before WooCommerce HTTP when no saved snapshot is available until before-state capture exists.
