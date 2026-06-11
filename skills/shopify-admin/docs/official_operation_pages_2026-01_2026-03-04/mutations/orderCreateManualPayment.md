---
title: orderCreateManualPayment - GraphQL Admin
description: >-
  Records a manual payment for an
  [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)
  that isn't fully paid. Use this mutation to track payments received outside
  the standard checkout process, such as cash, check, bank transfer, or other
  offline payment methods.


  You can specify the payment
  [amount](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-amount),
  [method
  name](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-paymentMethodName),
  and [when it was
  processed](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-processedAt).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment.md
---

# order​Create​Manual​Payment

mutation

Requires `write_orders` access scope. Also: The user must have mark\_orders\_as\_paid permission. The API client must be installed on a Shopify Plus store to use the amount field.

Records a manual payment for an [`Order`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order) that isn't fully paid. Use this mutation to track payments received outside the standard checkout process, such as cash, check, bank transfer, or other offline payment methods.

You can specify the payment [amount](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-amount), [method name](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-paymentMethodName), and [when it was processed](https://shopify.dev/docs/api/admin-graphql/latest/mutations/orderCreateManualPayment#arguments-processedAt).

## Arguments

* amount

  [Money​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MoneyInput)

  The manual payment amount to be created.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the order to create a manual payment for.

* payment​Method​Name

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The name of the payment method used for creating the payment. If none is provided, then the default manual payment method ('Other') will be used.

* processed​At

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The date and time ([ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format) when a manual payment was processed. If you're importing transactions from an app or another platform, then you can set processedAt to a date and time in the past to match when the original transaction was created.

***

## Order​Create​Manual​Payment​Payload returns

* order

  [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  The order recorded a manual payment.

* user​Errors

  [\[Order​Create​Manual​Payment​Order​Create​Manual​Payment​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/OrderCreateManualPaymentOrderCreateManualPaymentError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### orderCreateManualPayment reference
