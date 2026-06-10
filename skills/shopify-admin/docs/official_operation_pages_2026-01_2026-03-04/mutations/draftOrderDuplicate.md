---
title: draftOrderDuplicate - GraphQL Admin
description: Duplicates a draft order.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDuplicate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderDuplicate.md
---

# draft​Order​Duplicate

mutation

Requires `write_draft_orders` access scope. Also: The user must have access to manage draft orders.

Duplicates a draft order.

## Arguments

* id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the draft order to duplicate.

* draft​Order​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Deprecated

***

## Draft​Order​Duplicate​Payload returns

* draft​Order

  [Draft​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/DraftOrder)

  The newly duplicated draft order.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### draftOrderDuplicate reference
