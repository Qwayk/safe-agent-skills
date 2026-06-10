---
title: validationUpdate - GraphQL Admin
description: Update a validation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationUpdate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationUpdate.md
---

# validation​Update

mutation

Requires `write_validations` access scope.

Update a validation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID representing the validation to update.

* validation

  [Validation​Update​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ValidationUpdateInput)

  required

  The input fields to update a validation.

***

## Validation​Update​Payload returns

* user​Errors

  [\[Validation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ValidationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* validation

  [Validation](https://shopify.dev/docs/api/admin-graphql/latest/objects/Validation)

  The updated validation.

***

## Examples

* ### validationUpdate reference
