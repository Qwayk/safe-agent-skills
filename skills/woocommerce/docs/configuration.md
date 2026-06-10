# Configuration

This tool uses a local `.env` file and optional non-secret JSON config.

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
