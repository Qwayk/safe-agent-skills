---
title: customerPaymentMethodRevoke - GraphQL Admin
description: Revokes a customer's payment method.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodRevoke
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodRevoke.md
---

# customer​Payment​Method​Revoke

mutation

Requires `write_customers` access scope. Also: Requires `write_customer_payment_methods` scope.

Revokes a customer's payment method.

## Arguments

* customer​Payment​Method​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer payment method to be revoked.

***

## Customer​Payment​Method​Revoke​Payload returns

* revoked​Customer​Payment​Method​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the revoked customer payment method.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerPaymentMethodRevoke reference
