---
title: returnReopen - GraphQL Admin
description: Reopens a closed return.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnReopen'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/returnReopen.md'
---

# return​Reopen

mutation

Requires `write_returns` access scope or `write_marketplace_returns` access scope.

Reopens a closed return.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the return to reopen.

***

## Return​Reopen​Payload returns

* return

  [Return](https://shopify.dev/docs/api/admin-graphql/latest/objects/Return)

  The reopened return.

* user​Errors

  [\[Return​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReturnUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### returnReopen reference
