---
title: orderEditRemoveLineItemDiscount - GraphQL Admin
description: Removes a line item discount that was applied as part of an order edit.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveLineItemDiscount
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveLineItemDiscount.md
---

# order​Edit​Remove​Line​Item​Discount

mutation

Requires `write_order_edits` access scope. Also: The user must have apply\_discounts\_to\_orders permission.

Deprecated. Use [orderEditRemoveDiscount](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditRemoveDiscount) instead.

Removes a line item discount that was applied as part of an order edit.

## Arguments

* discount​Application​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated discount application](https://shopify.dev/api/admin-graphql/latest/interfaces/calculateddiscountapplication) to remove.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session to edit. This is the edit from which the line item discount is removed.

***

## Order​Edit​Remove​Line​Item​Discount​Payload returns

* calculated​Line​Item

  [Calculated​Line​Item](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedLineItem)

  The calculated line item after removal of the discount.

* calculated​Order

  [Calculated​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/CalculatedOrder)

  An order with the edits applied but not saved.

* order​Edit​Session

  [Order​Edit​Session](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderEditSession)

  The order edit session with the edits applied but not saved.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderEditRemoveLineItemDiscount reference
