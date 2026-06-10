---
title: paymentCustomizationUpdate - GraphQL Admin
description: Updates a payment customization.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationUpdate.md
---

# payment​Customization​Update

mutation

Requires `write_payment_customizations` access scope.

Updates a payment customization.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The global ID of the payment customization.

* payment​Customization

  [Payment​Customization​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PaymentCustomizationInput)

  required

  The input data used to update the payment customization.

***

## Payment​Customization​Update​Payload returns

* payment​Customization

  [Payment​Customization](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomization)

  Returns the updated payment customization.

* user​Errors

  [\[Payment​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### paymentCustomizationUpdate reference
