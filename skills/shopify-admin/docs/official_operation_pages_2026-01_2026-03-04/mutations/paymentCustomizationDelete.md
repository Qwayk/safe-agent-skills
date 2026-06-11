---
title: paymentCustomizationDelete - GraphQL Admin
description: Deletes a payment customization.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationDelete
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationDelete.md
---

# payment​Customization​Delete

mutation

Requires `write_payment_customizations` access scope.

Deletes a payment customization.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The global ID of the payment customization.

***

## Payment​Customization​Delete​Payload returns

* deleted​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Returns the deleted payment customization ID.

* user​Errors

  [\[Payment​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### paymentCustomizationDelete reference
