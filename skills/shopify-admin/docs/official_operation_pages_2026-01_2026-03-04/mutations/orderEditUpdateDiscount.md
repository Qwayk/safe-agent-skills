---
title: orderEditUpdateDiscount - GraphQL Admin
description: >-
  Updates a manual line level discount on the current order edit. For more
  information on how to use the GraphQL Admin API to edit an existing order,
  refer to [Edit existing
  orders](https://shopify.dev/apps/fulfillment/order-management-apps/order-editing).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditUpdateDiscount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditUpdateDiscount.md
---

# order​Edit​Update​Discount

mutation

Requires `write_order_edits` access scope. Also: The user must have apply\_discounts\_to\_orders permission.

Updates a manual line level discount on the current order edit. For more information on how to use the GraphQL Admin API to edit an existing order, refer to [Edit existing orders](https://shopify.dev/apps/fulfillment/order-management-apps/order-editing).

## Arguments

* discount

  [Order​Edit​Applied​Discount​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/OrderEditAppliedDiscountInput)

  required

  The updated discount.

* discount​Application​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated discount application](https://shopify.dev/api/admin-graphql/latest/interfaces/calculateddiscountapplication) to update.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit. This is the edit used to update the discount.

***

## Order​Edit​Update​Discount​Payload returns

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  An order with the edits applied but not saved.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[Order​Edit​Update​Discount​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditUpdateDiscountUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderEditUpdateDiscount reference
