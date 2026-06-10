---
title: orderEditSetQuantity - GraphQL Admin
description: >-
  Sets the quantity of a line item on an order that's being edited. Use this
  mutation to increase, decrease, or remove items by adjusting their quantities.


  Setting the quantity to zero effectively removes the line item from the order.
  The item still exists as a data structure with zero quantity. When decreasing
  quantities, you can optionally restock the removed items to inventory by
  setting the `restock` parameter to `true`.


  Learn more about [editing workflows for existing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditSetQuantity
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditSetQuantity.md
---

# order​Edit​Set​Quantity

mutation

Requires `write_order_edits` access scope.

Sets the quantity of a line item on an order that's being edited. Use this mutation to increase, decrease, or remove items by adjusting their quantities.

Setting the quantity to zero effectively removes the line item from the order. The item still exists as a data structure with zero quantity. When decreasing quantities, you can optionally restock the removed items to inventory by setting the `restock` parameter to `true`.

Learn more about [editing workflows for existing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit. The edit changes the quantity on the line item.

* line​Item​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the calculated line item to edit.

* quantity

  [Int!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  required

  The new quantity to set for the line item. This value cannot be negative.

* restock

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether or not to restock the line item when the updated quantity is less than the original quantity.

* location​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Deprecated

***

## Order​Edit​Set​Quantity​Payload returns

* calculated​Line​Item

  [Calculated​Line​Item](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedLineItem)

  The calculated line item with the edits applied but not saved.

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  The calculated order with the edits applied but not saved.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderEditSetQuantity reference
