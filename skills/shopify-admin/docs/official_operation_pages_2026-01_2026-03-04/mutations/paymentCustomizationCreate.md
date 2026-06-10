---
title: paymentCustomizationCreate - GraphQL Admin
description: Creates a payment customization.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationCreate.md
---

# payment​Customization​Create

mutation

Requires `write_payment_customizations` access scope.

Creates a payment customization.

## Arguments

* payment​Customization

  [Payment​Customization​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/PaymentCustomizationInput)

  required

  The input data used to create the payment customization.

***

## Payment​Customization​Create​Payload returns

* payment​Customization

  [Payment​Customization](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomization)

  Returns the created payment customization.

* user​Errors

  [\[Payment​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### paymentCustomizationCreate reference
