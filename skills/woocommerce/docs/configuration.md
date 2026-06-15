# Configuration

WooCommerce configuration is the local setup an agent needs before it can review products, orders, customers, coupons, and store data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which WooCommerce values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Use a local `.env` file for private values and optional JSON config for non-secret defaults.

Use `--config <file>` for machine defaults. It can include any non-secret
configuration keys only.

## Required values

- `WOOCOMMERCE_STORE_URL`
- `WOOCOMMERCE_CONSUMER_KEY`
- `WOOCOMMERCE_CONSUMER_SECRET`

## Optional values

- `WOOCOMMERCE_API_BASE_URL`
  Use this only if your REST base differs from the normal `/wp-json/wc/v3`.
- `WOOCOMMERCE_QUERY_STRING_AUTH`
  Set to `true` when the server strips `Authorization` headers.
- `WOOCOMMERCE_VERIFY_SSL`
  Leave this as `true` except for local self-signed test stores.
- `WOOCOMMERCE_TIMEOUT_S`
  Default is `30`.

## JSON config example

```json
{
  "WOOCOMMERCE_STORE_URL": "https://shop.example.com",
  "WOOCOMMERCE_QUERY_STRING_AUTH": true,
  "WOOCOMMERCE_VERIFY_SSL": true,
  "WOOCOMMERCE_TIMEOUT_S": 45
}
```

The JSON file must not include:

- `WOOCOMMERCE_CONSUMER_KEY`
- `WOOCOMMERCE_CONSUMER_SECRET`

CLI flags always win over config values.
