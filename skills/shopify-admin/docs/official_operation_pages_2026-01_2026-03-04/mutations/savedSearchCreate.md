---
title: savedSearchCreate - GraphQL Admin
description: Creates a saved search.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/savedSearchCreate.md
---

# saved​Search​Create

mutation

Creates a saved search.

## Arguments

* input

  [Saved​Search​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/SavedSearchCreateInput)

  required

  Specifies the input fields for a saved search.

***

## Saved​Search​Create​Payload returns

* saved​Search

  [Saved​Search](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch)

  The saved search that was created.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### savedSearchCreate reference
