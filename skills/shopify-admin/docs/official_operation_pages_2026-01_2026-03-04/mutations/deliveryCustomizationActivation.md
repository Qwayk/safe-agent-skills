---
title: deliveryCustomizationActivation - GraphQL Admin
description: Activates and deactivates delivery customizations.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryCustomizationActivation
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryCustomizationActivation.md
---

# delivery​Customization​Activation

mutation

Requires `write_delivery_customizations` access scope.

Activates and deactivates delivery customizations.

## Arguments

* enabled

  [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  required

  The enabled status of the delivery customizations.

* ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The global IDs of the delivery customizations.

***

## Delivery​Customization​Activation​Payload returns

* ids

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The IDs of the updated delivery customizations.

* user​Errors

  [\[Delivery​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliveryCustomizationActivation reference
