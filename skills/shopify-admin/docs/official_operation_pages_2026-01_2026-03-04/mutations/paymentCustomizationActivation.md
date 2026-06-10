---
title: paymentCustomizationActivation - GraphQL Admin
description: Activates and deactivates payment customizations.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationActivation
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/paymentCustomizationActivation.md
---

# payment​Customization​Activation

mutation

Requires `write_payment_customizations` access scope.

Activates and deactivates payment customizations.

## Arguments

* enabled

  [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  required

  The enabled status of the payment customizations.

* ids

  [\[ID!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The global IDs of the payment customizations.

***

## Payment​Customization​Activation​Payload returns

* ids

  [\[String!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The IDs of the updated payment customizations.

* user​Errors

  [\[Payment​Customization​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PaymentCustomizationError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### paymentCustomizationActivation reference
