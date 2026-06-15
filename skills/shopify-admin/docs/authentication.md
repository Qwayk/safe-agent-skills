# Authentication

Shopify Admin authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because products, orders, customers, discounts, themes, publications, and store settings can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Shopify Admin environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Authentication notes

What this means in practice:

## Setup details

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
