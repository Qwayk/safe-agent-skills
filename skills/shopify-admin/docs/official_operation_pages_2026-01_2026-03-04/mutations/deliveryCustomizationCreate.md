---
title: deliveryCustomizationCreate - GraphQL Admin
description: Creates a delivery customization.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryCustomizationCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/deliveryCustomizationCreate.md
---

# delivery​Customization​Create

mutation

Requires `write_delivery_customizations` access scope.

Creates a delivery customization.

## Arguments

* delivery​Customization

  [Delivery​Customization​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/DeliveryCustomizationInput)

  required

  The input data used to create the delivery customization.

***

## Delivery​Customization​Create​Payload returns

* delivery​Customization

  [Delivery​Customization](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCustomization)

  Returns the created delivery customization.

* user​Errors

  [\[Delivery​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### deliveryCustomizationCreate reference
