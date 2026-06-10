---
title: deliveryProfileRemove - GraphQL Admin
description: Enqueue the removal of a delivery profile.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryProfileRemove
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryProfileRemove.md
---

# delivery​Profile​Remove

mutation

Requires Any of `shipping` access scopes or `manage_delivery_settings` user permission.

Enqueue the removal of a delivery profile.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the delivery profile to remove.

***

## Delivery​Profile​Remove​Payload returns

* job

  [Job](https://shopify.dev/docs/api/admin-graphql/latest/objects/Job)

  The delivery profile deletion job triggered by the mutation.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliveryProfileRemove reference
