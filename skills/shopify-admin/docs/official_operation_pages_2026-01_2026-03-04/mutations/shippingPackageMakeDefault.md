---
title: shippingPackageMakeDefault - GraphQL Admin
description: >-
  Set a shipping package as the default.

  The default shipping package is the one used to calculate shipping costs on
  checkout.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shippingPackageMakeDefault
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/shippingPackageMakeDefault.md
---

# shipping​Package​Make​Default

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Set a shipping package as the default. The default shipping package is the one used to calculate shipping costs on checkout.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the shipping package to set as the default.

***

## Shipping​Package​Make​Default​Payload returns

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### shippingPackageMakeDefault reference
