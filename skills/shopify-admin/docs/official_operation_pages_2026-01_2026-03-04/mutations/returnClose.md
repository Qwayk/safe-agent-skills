---
title: returnClose - GraphQL Admin
description: >-
  Indicates a return is complete, either when a refund has been made and items
  restocked,

  or simply when it has been marked as returned in the system.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnClose'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnClose.md'
---

# return​Close

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Indicates a return is complete, either when a refund has been made and items restocked, or simply when it has been marked as returned in the system.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the return to close.

***

## Return​Close​Payload returns

* return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The closed return.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### returnClose reference
