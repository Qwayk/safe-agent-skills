---
title: customerPaymentMethodCreditCardUpdate - GraphQL Admin
description: Updates the credit card payment method for a customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodCreditCardUpdate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodCreditCardUpdate.md
---

# customer​Payment​Method​Credit​Card​Update

mutation

Requires `write_customers` access scope. Also: Requires `write_customer_payment_methods` scope.

Updates the credit card payment method for a customer.

## Arguments

* billing​Address

  [Mailing​Address​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MailingAddressInput)

  required

  The billing address.

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer payment method.

* session​Id

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The Cardserver session ID.

***

## Customer​Payment​Method​Credit​Card​Update​Payload returns

* customer​Payment​Method

  [Customer​Payment​Method](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethod)

  The customer payment method.

* processing

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  If the card verification result is processing. When this is true, customer\_payment\_method will be null.

* user​Errors

  [\[User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/UserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerPaymentMethodCreditCardUpdate reference
