---
title: returnCancel - GraphQL Admin
description: |-
  Cancels a return and restores the items back to being fulfilled.
  Canceling a return is only available before any work has been done
  on the return (such as an inspection or refund).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnCancel'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnCancel.md'
---

# return​Cancel

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Cancels a return and restores the items back to being fulfilled. Canceling a return is only available before any work has been done on the return (such as an inspection or refund).

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the return to cancel.

* notify​Customer

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  DeprecatedDefault:false

***

## Return​Cancel​Payload returns

* return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The canceled return.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### returnCancel reference
