---
title: customerPaymentMethodCreditCardCreate - GraphQL Admin
description: >-
  Creates a credit card payment method for a customer using a session id.

  These values are only obtained through card imports happening from a PCI
  compliant environment.

  Please use customerPaymentMethodRemoteCreate if you are not managing credit
  cards directly.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodCreditCardCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodCreditCardCreate.md
---

# customer​Payment​Method​Credit​Card​Create

mutation

Requires `write_customers` access scope. Also: Requires `write_customer_payment_methods` scope.

Creates a credit card payment method for a customer using a session id. These values are only obtained through card imports happening from a PCI compliant environment. Please use customerPaymentMethodRemoteCreate if you are not managing credit cards directly.

## Arguments

* billing​Address

  [Mailing​Address​Input!](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MailingAddressInput)

  required

  The billing address.

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer.

* session​Id

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The Cardserver session ID. Obtained by storing card data with Shopify's Cardsink. Exchanging raw card data for a session ID must be done in a PCI complaint environment.

***

## Customer​Payment​Method​Credit​Card​Create​Payload returns

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

* ### customerPaymentMethodCreditCardCreate reference
