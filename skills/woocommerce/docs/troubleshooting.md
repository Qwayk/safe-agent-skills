# Troubleshooting

When WooCommerce stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing products, orders, customers, coupons, and store data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the WooCommerce error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
