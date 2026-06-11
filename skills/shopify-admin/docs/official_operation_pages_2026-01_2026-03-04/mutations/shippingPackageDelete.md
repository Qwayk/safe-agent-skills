---
title: shippingPackageDelete - GraphQL Admin
description: Deletes a shipping package.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shippingPackageDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shippingPackageDelete.md
---

# shipping​Package​Delete

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Deletes a shipping package.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the shipping package to remove.

***

## Shipping​Package​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the deleted shipping package.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### shippingPackageDelete reference
