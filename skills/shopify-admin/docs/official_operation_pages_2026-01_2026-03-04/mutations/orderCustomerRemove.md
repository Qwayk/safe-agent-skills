---
title: orderCustomerRemove - GraphQL Admin
description: Removes customer from an order.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCustomerRemove
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCustomerRemove.md
---

# order​Customer​Remove

mutation

Requires `write_orders` access scope. Also: The user must have permission to manage the order.

Removes customer from an order.

## Arguments

* order​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the order having its customer removed.

***

## Order​Customer​Remove​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order that had its customer removed.

* user​Errors

  [\[Order​Customer​Remove​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderCustomerRemoveUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderCustomerRemove reference
