---
title: savedSearchUpdate - GraphQL Admin
description: Updates a saved search.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchUpdate.md
---

# saved​Search​Update

mutation

Updates a saved search.

## Arguments

* input

  [Saved​Search​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SavedSearchUpdateInput)

  required

  The input fields to update a saved search.

***

## Saved​Search​Update​Payload returns

* saved​Search

  [Saved​Search](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch)

  The saved search that was updated.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### savedSearchUpdate reference
