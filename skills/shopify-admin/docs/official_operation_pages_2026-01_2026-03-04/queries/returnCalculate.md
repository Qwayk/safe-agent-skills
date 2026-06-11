---
title: returnCalculate - GraphQL Admin
description: >-
  Calculates the financial outcome of a
  [`Return`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)
  without creating it. Use this query to preview return costs before initiating
  the actual return process.


  The calculation provides detailed breakdowns of refund amounts, taxes,
  [`RestockingFee`](https://shopify.dev/docs/api/admin-graphql/latest/objects/RestockingFee)
  charges, return shipping fees, and order-level discount adjustments based on
  the
  [`FulfillmentLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentLineItem)
  objects that customers select for return.


  Learn more about building for [return
  management](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/returnCalculate'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/returnCalculate.md'
---

# return​Calculate

query

Requires `read_returns` access scope or `read_marketplace_returns` access scope. Also: The shop must have access to exchanges.

Calculates the financial outcome of a [`Return`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return) without creating it. Use this query to preview return costs before initiating the actual return process.

The calculation provides detailed breakdowns of refund amounts, taxes, [`RestockingFee`](https://shopify.dev/docs/api/admin-graphql/latest/objects/RestockingFee) charges, return shipping fees, and order-level discount adjustments based on the [`FulfillmentLineItem`](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentLineItem) objects that customers select for return.

Learn more about building for [return management](https://shopify.dev/docs/apps/build/orders-fulfillment/returns-apps/build-return-management).

## Arguments

* input

  [Calculate​Return​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/CalculateReturnInput)

  required

  The input fields for calculating a return.

***

## Possible returns

* Calculated​Return

  [Calculated​Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedReturn)

  A calculated return.

  * exchange​Line​Items

    [\[Calculated​Exchange​Line​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedExchangeLineItem)

    non-null

    A list of calculated exchange line items.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * return​Line​Items

    [\[Calculated​Return​Line​Item!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedReturnLineItem)

    non-null

    A list of calculated return line items.

  * return​Shipping​Fee

    [Calculated​Return​Shipping​Fee](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedReturnShippingFee)

    The calculated return shipping fee.

***

## Examples

* ### returnCalculate reference
