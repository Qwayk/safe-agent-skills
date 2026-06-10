---
title: orderEditCommit - GraphQL Admin
description: >-
  Applies staged changes from an order editing session to the original order.
  This finalizes all modifications made during the edit session, including
  changes to line items, quantities, discounts, and shipping lines.


  Order editing follows a three-step workflow: start with
  [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin)
  to create an editing session, apply changes using various orderEdit mutations,
  and then save the changes with the
  [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit)
  mutation. The mutation can optionally notify the customer of changes and add
  staff notes for internal tracking.


  You can only edit unfulfilled line items. If an edit changes the total order
  value, then the customer might need to pay a balance or receive a refund.


  Learn more about [editing existing
  orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit.md
---

# order​Edit​Commit

mutation

Requires `write_order_edits` access scope.

Applies staged changes from an order editing session to the original order. This finalizes all modifications made during the edit session, including changes to line items, quantities, discounts, and shipping lines.

Order editing follows a three-step workflow: start with [`orderEditBegin`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditBegin) to create an editing session, apply changes using various orderEdit mutations, and then save the changes with the [`orderEditCommit`](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderEditCommit) mutation. The mutation can optionally notify the customer of changes and add staff notes for internal tracking.

You can only edit unfulfilled line items. If an edit changes the total order value, then the customer might need to pay a balance or receive a refund.

Learn more about [editing existing orders](https://shopify.dev/docs/apps/build/orders-fulfillment/order-management-apps/edit-orders).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the [calculated order](https://shopify.dev/api/admin-graphql/latest/objects/calculatedorder) or the order edit session that will have its changes applied to the order.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Whether to notify the customer or not.

* staff​Note

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Note for staff members.

***

## Order​Edit​Commit​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order with changes applied.

* success​Messages

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  Messages to display to the user after the staged changes are commmitted.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderEditCommit reference
