# Connect your Shopify Admin account

Shopify Admin needs local store credentials before an agent can inspect products, orders, customers, content, and store settings.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a store or product read before asking for catalog, order, customer, or theme changes.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the required fields:
   - `SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com`
   - `SHOPIFY_ADMIN_ACCESS_TOKEN=...`
   - `SHOPIFY_ADMIN_API_VERSION=2026-01`

## Step 2: Get the API key/token (tool-specific)

You need a Shopify **custom app** Admin API access token.

1. In Shopify Admin, open **Settings** → **Apps and sales channels**.
2. Click **Develop apps** (you may need to enable app development for your store).
3. Create a **custom app** (or open an existing one).
4. Configure **Admin API access scopes** appropriate for what you want to do:
   - Queries typically require read scopes (example: products, orders).
   - Mutations require write scopes and are riskier.
5. Install the app (if required by Shopify) and generate the **Admin API access token**.
6. Copy/paste into `.env`:
   - `SHOPIFY_SHOP_DOMAIN`: your store domain (example: `your-shop.myshopify.com`)
   - `SHOPIFY_ADMIN_ACCESS_TOKEN`: the Admin API access token value
   - `SHOPIFY_ADMIN_API_VERSION`: `2026-01` (pinned; required for full coverage guarantees)

Never paste the token into chat.

## Step 3: What to ask your AI agent (examples)

Ask your agent to start with a read-only check, then show a preview. Mutation apply requires explicit no-snapshot approval today until operation-specific saved snapshot support is available.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “List all supported Shopify Admin operations for this tool’s pinned version.”
- “List my products and export a clean product list to a file.”
- “Create a new product with these variants and prices, but do a dry-run reviewed plan first.”
- “Draft a price update plan for these SKUs and explain why live apply requires explicit no-snapshot approval today.”
- “Export orders from the last 30 days.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Create dry-run metadata update plans from this spreadsheet.”
- “Do a dry-run reviewed plan first, then ask me before any Shopify mutation runs.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Wrong key type (example: read-only key vs admin key)
- Network or permission restrictions in the connected account

See `docs/troubleshooting.md` for common errors and fixes.
