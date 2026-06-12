# Use cases

Use this page when you want practical Shopify Admin jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this helps with store work

Shopify work is usually about a live store, not an abstract database. A small mistake can change what shoppers see, what staff fulfill, or what customers receive.

This skill is useful when you want the agent to inspect the store first, then prepare a clear plan for product, inventory, customer, order, discount, or collection work before anything is applied.

## Good jobs to give the agent

- “Show me products that are missing tags, images, or descriptions.”
- “Export recent orders with line items and totals for a support review.”
- “Find products in this collection and draft the changes before applying them.”
- “Check which discounts are active and when they expire.”
- “Review inventory for these SKUs at this location.”
- “Prepare a plan for product metadata updates from this spreadsheet.”
- “Find customer records that match this segment and export the IDs.”

## Specific examples

- Products: “Create a dry-run plan for a new product with variants and prices.”
- Products: “Draft a plan to update product titles, descriptions, tags, and media for these product IDs.”
- Inventory: “Set on-hand inventory levels for these SKUs at this location.”
- Orders: “Export orders from the last 30 days with line items and totals, then save to a file.”
- Refunds: “Draft a refund mutation plan, review the recovery limit, then approve the exact live apply only if it still looks right.”
- Discounts: “Create a dry-run plan for a discount code with these rules and an end date.”
- Collections: “Plan adding these products to this collection and removing others.”
- Customers: “Find customers who match this segment and export their IDs.”

## What the agent should show you

When you ask for a change, the agent should:

1. Show a dry-run preview of what would change.
2. Explain any extra mutation gates, including `--ack-no-snapshot` when no saved snapshot exists.
3. Apply only after explicit approval.
4. Report the receipt or Shopify error clearly.
5. Point to the saved plan and run artifacts when they are available.
