# Authentication

This tool uses Shopify **Admin API access tokens** (custom app) for Admin GraphQL requests.

What this means in practice:
- You create a “custom app” inside your Shopify Admin.
- Shopify gives you an Admin API access token for that app.
- You paste that token into your local `.env` file (never into chat).

## Required env keys

- `SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com`
- `SHOPIFY_ADMIN_ACCESS_TOKEN=...`
- `SHOPIFY_ADMIN_API_VERSION=2026-01`

Notes:
- `SHOPIFY_SHOP_DOMAIN` should not include `https://` and should typically end with `.myshopify.com`.
- The access token must have the scopes needed for what you want to do. Read-only work needs read scopes; changing data needs write scopes.

## Smoke test

Run:

```bash
shopify-admin-api-tool --output json auth check
```
