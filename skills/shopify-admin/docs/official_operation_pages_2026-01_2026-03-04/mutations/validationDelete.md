---
title: validationDelete - GraphQL Admin
description: Deletes a validation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationDelete'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationDelete.md
---

# validation​Delete

mutation

Requires `write_validations` access scope.

Deletes a validation.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID representing the installed validation.

***

## Validation​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Returns the deleted validation ID.

* user​Errors

  [\[Validation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ValidationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### validationDelete reference
