# What you can do with WooCommerce

WooCommerce work usually means checking a live store before someone changes products, orders, coupons, customers, shipping, tax, or checkout settings.

This skill can help with store reviews, catalog cleanup, order checks, coupon planning, customer or review research, and careful batch-change plans. The value is practical: find the exact store data that matters, explain it clearly, and stop before risky changes until a human approves.

If you need setup first, start with [Connect your WooCommerce store](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good first asks

- "Check the WooCommerce connection, then show the store settings that matter for this review."
- "List active products and flag anything missing a price, stock status, category, image, or short description."
- "Find this order and explain its status, payment, shipping, and customer details."
- "Show shipping zones, payment gateways, taxes, countries, currencies, and checkout settings before we change anything."
- "Preview a coupon for this sale, but do not create it yet."

## Store-owner jobs

Good WooCommerce work often starts with a real store question:

- "Which products look incomplete before we launch the sale?"
- "Which orders need attention because payment, shipping, or fulfillment looks unclear?"
- "Which coupons are active, expired, or risky before a campaign starts?"
- "Which customers or reviews match these rules?"
- "Which settings could explain a checkout or shipping issue?"
- "Can you prepare a batch product update from this CSV and stop before applying it?"

These jobs are useful because they connect API data to what a store owner actually needs to decide.

## Catalog cleanup

For product and category work, a good flow is:

1. Pull the relevant products, variations, categories, tags, or attributes.
2. Flag missing or inconsistent data.
3. Group the fixes by risk: easy metadata, price or stock changes, and customer-facing changes.
4. Create a dry-run plan for the exact products that need updates.
5. Wait for approval before changing the live store.

The agent should not hide risky changes inside a big batch.

## Orders, customers, and checkout

For customer-facing issues, good asks include:

- "Find this customer and show recent orders without changing anything."
- "Check the order status history and explain what probably happened."
- "Review payment gateways and shipping zones for this region."
- "List taxes or currencies that may affect this checkout problem."
- "Prepare a refund, status, or coupon change plan, but stop before apply."

The answer should be careful with customer data and should name the order, customer, product, coupon, or setting being discussed.

## What good output looks like

A useful WooCommerce answer should include:

- the store or connection checked
- the products, orders, customers, coupons, reviews, settings, or zones reviewed
- a short summary of what needs attention
- the exact targets for any proposed change
- the approval gate before live store writes
- proof after apply when a reviewed change is allowed

## Honest limits

WooCommerce stores vary by plugins, settings, permissions, and custom fields. If the API cannot see a feature or a plugin-owned setting, the agent should say that plainly instead of pretending every store works the same way.
