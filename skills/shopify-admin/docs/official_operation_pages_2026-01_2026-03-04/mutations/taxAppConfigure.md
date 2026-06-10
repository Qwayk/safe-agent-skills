---
title: taxAppConfigure - GraphQL Admin
description: Allows tax app configurations for tax partners.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/taxAppConfigure'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/taxAppConfigure.md
---

# tax​App​Configure

mutation

Requires `write_taxes` access scope. Also: The caller must be a tax calculations app.

Allows tax app configurations for tax partners.

## Arguments

* ready

  [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  required

  Configures whether the tax app is correctly configured and ready to be used.

***

## Tax​App​Configure​Payload returns

* tax​App​Configuration

  [Tax​App​Configuration](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxAppConfiguration)

  The updated tax app configuration.

* user​Errors

  [\[Tax​App​Configure​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxAppConfigureUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### taxAppConfigure reference
