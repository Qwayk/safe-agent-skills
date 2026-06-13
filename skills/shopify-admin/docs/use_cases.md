# What you can do with Shopify Admin

Shopify Admin work usually starts with a live-store question: which products need cleanup, which orders need review, which inventory numbers look wrong, which customers match a segment, or which discount is still active.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps an agent read store data, export useful review files, and prepare mutation plans before anything touches products, variants, inventory, orders, customers, collections, discounts, or metadata.

## Good jobs to give the agent

### Store, catalog, and product cleanup

- "Show store details and list the products that are missing tags, images, descriptions, vendors, or SEO fields."
- "Find products in this collection and draft the changes before applying them."
- "Review variants and prices for these product IDs."
- "Prepare a plan for product title, description, tag, media, or metadata updates from this spreadsheet."
- "List collections and show which products would be added or removed."

### Orders, customers, and support review

- "Export recent orders with line items, totals, fulfillment status, and customer IDs for support review."
- "Find orders from the last 30 days that look unpaid, unfulfilled, canceled, or refunded."
- "Search customer records that match this segment and export the IDs."
- "Explain what happened with this order before support replies to the customer."
- "Prepare a refund mutation plan and show the recovery limit before any live step."

### Inventory, discounts, and merchandising

- "Review inventory for these SKUs at this location."
- "Find products with low stock or mismatched inventory numbers."
- "Check which discounts are active, when they expire, and what they apply to."
- "Draft a discount code plan with these rules and an end date."
- "Review checkout, campaign, or merchandising data before a sale starts."

### Careful mutation planning

- "Create a dry-run plan for a new product with variants and prices."
- "Draft a metadata update plan for these product, variant, customer, or order IDs."
- "Show exactly which Shopify mutation would run and what approval is needed."
- "Tell me when a custom return shape could expose private customer data."

## What the agent should show you

- Whether it is reading from the intended shop and pinned Admin API version.
- The product, variant, inventory item, order, customer, collection, discount, or mutation it checked.
- A short explanation before raw Shopify data, especially for support and finance questions.
- A dry-run plan before any create, update, delete, refund, inventory, discount, collection, or metadata mutation.
- Stronger approval gates for irreversible, customer-impacting, or no-snapshot work.
- The saved plan, receipt, Shopify error, or run history after the request.

## Good first Shopify path

Start with `auth check`, read store details, export recent orders and products, then inspect one product or order end to end before planning any mutation.
