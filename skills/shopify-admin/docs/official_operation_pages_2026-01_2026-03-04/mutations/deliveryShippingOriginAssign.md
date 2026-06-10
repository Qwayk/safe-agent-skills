---
title: deliveryShippingOriginAssign - GraphQL Admin
description: >-
  Assigns a location as the shipping origin while using legacy compatibility
  mode for multi-location delivery profiles.

  Deprecated as of 2026-04 and will be removed in a future version as single
  origin shipping mode has been retired.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryShippingOriginAssign
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryShippingOriginAssign.md
---

# delivery​Shipping​Origin​Assign

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Deprecated. Single origin shipping mode is no longer supported.

Assigns a location as the shipping origin while using legacy compatibility mode for multi-location delivery profiles. Deprecated as of 2026-04 and will be removed in a future version as single origin shipping mode has been retired.

## Arguments

* location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the location to assign as the shipping origin.

***

## Delivery​Shipping​Origin​Assign​Payload returns

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliveryShippingOriginAssign reference
