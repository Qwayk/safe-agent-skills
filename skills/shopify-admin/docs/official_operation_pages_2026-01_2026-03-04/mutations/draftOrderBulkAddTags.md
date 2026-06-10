---
title: draftOrderBulkAddTags - GraphQL Admin
description: Adds tags to multiple draft orders.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderBulkAddTags
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/draftOrderBulkAddTags.md
---

# draft​Order​Bulk​Add​Tags

mutation

Requires `write_draft_orders` access scope. Also: The user must have access to manage draft orders.

Adds tags to multiple draft orders.

## Arguments

* ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The IDs of the draft orders to add tags to.

* saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the draft order saved search for filtering draft orders on.

* search

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The conditions for filtering draft orders on. See the detailed [search syntax](https://shopify.dev/api/usage/search-syntax).

* tags

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  List of tags to be added.

***

## Draft​Order​Bulk​Add​Tags​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The asynchronous job for adding tags to the draft orders.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### draftOrderBulkAddTags reference
