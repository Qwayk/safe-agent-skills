---
title: orderEditRemoveDiscount - GraphQL Admin
description: >-
  Removes a discount on the current order edit. For more information on how to
  use the GraphQL Admin API to edit an existing order, refer to [Edit existing
  orders](https://shopify.dev/apps/fulfillment/order-management-apps/order-editing).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveDiscount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveDiscount.md
---

# order​Edit​Remove​Discount

mutation

Requires `write_order_edits` access scope. Also: The user must have apply\_discounts\_to\_orders permission.

Removes a discount on the current order edit. For more information on how to use the GraphQL Admin API to edit an existing order, refer to [Edit existing orders](https://shopify.dev/apps/fulfillment/order-management-apps/order-editing).

## Arguments

* discount​Application​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated discount application](https://shopify.dev/api/admin-graphql/latest/interfaces/calculateddiscountapplication) to remove.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit. This is the edit from which the discount is removed.

***

## Order​Edit​Remove​Discount​Payload returns

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  An order with the edits applied but not saved.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[Order​Edit​Remove​Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditRemoveDiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderEditRemoveDiscount reference
