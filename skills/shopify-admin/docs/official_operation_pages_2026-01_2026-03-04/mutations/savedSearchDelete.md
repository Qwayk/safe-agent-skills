---
title: savedSearchDelete - GraphQL Admin
description: Delete a saved search.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchDelete.md
---

# saved​Search​Delete

mutation

Delete a saved search.

## Arguments

* input

  [Saved​Search​Delete​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SavedSearchDeleteInput)

  required

  The input fields to delete a saved search.

***

## Saved​Search​Delete​Payload returns

* deleted​Saved​Search​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the saved search that was deleted.

* shop

  [Shop!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Shop)

  non-null

  The shop of the saved search that was deleted.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### savedSearchDelete reference
