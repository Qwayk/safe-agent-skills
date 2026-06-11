---
title: bulkOperationCancel - GraphQL Admin
description: >-
  Starts the cancelation process of a running bulk operation.


  There may be a short delay from when a cancelation starts until the operation
  is actually canceled.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationCancel
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/bulkOperationCancel.md
---

# bulk​Operation​Cancel

mutation

Starts the cancelation process of a running bulk operation.

There may be a short delay from when a cancelation starts until the operation is actually canceled.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the bulk operation to cancel.

***

## Bulk​Operation​Cancel​Payload returns

* bulk​Operation

  [Bulk​Operation](https://shopify.dev/docs/api/admin-graphql/latest/objects/BulkOperation)

  The bulk operation to be canceled.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### bulkOperationCancel reference
