---
title: validationCreate - GraphQL Admin
description: Creates a validation.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/validationCreate.md
---

# validation​Create

mutation

Requires `write_validations` access scope.

Creates a validation.

## Arguments

* validation

  [Validation​Create​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ValidationCreateInput)

  required

  The input fields for a new validation.

***

## Validation​Create​Payload returns

* user​Errors

  [\[Validation​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ValidationUserError)

  non-null

  The list of errors that occurred from executing the mutation.

* validation

  [Validation](https://shopify.dev/docs/api/admin-graphql/latest/objects/Validation)

  The created validation.

***

## Examples

* ### validationCreate reference
