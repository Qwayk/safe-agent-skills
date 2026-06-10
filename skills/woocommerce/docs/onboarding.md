# Onboarding

This page is for first-time setup.
You only need your store URL and a WooCommerce REST API key pair.

## Step by step

1. Create a local `.env` file:

```bash
qwayk-woocommerce-safe-agent-cli onboarding
```

2. Open WordPress admin.
3. Go to `WooCommerce > Settings > Advanced > REST API`.
4. Create a new key with `Read/Write` access.
5. Fill these values in `.env`:

```dotenv
WOOCOMMERCE_STORE_URL=https://shop.example.com
WOOCOMMERCE_CONSUMER_KEY=ck_...
WOOCOMMERCE_CONSUMER_SECRET=cs_...
```

6. If your server strips the `Authorization` header, also set:

```dotenv
WOOCOMMERCE_QUERY_STRING_AUTH=true
```

7. Run the connection check:

```bash
qwayk-woocommerce-safe-agent-cli --output json auth check
```

## What to ask your AI agent

- “Check if this WooCommerce tool is connected.”
- “List all products.”
- “Preview a new coupon before creating it.”
- “Show me all shipping zones.”

Write apply currently requires explicit no-snapshot approval before WooCommerce HTTP when the tool cannot save real before-state.
