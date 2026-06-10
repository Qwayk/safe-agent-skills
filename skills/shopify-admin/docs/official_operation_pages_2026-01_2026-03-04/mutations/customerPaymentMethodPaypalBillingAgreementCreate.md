---
title: customerPaymentMethodPaypalBillingAgreementCreate - GraphQL Admin
description: Creates a PayPal billing agreement for a customer.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodPaypalBillingAgreementCreate
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerPaymentMethodPaypalBillingAgreementCreate.md
---

# customer​Payment​Method​Paypal​Billing​Agreement​Create

mutation

Requires `write_customers` access scope. Also: Requires `write_customer_payment_methods` scope.

Creates a PayPal billing agreement for a customer.

## Arguments

* billing​Address

  [Mailing​Address​Input](https://shopify.dev/docs/api/admin-graphql/latest/input-objects/MailingAddressInput)

  The billing address.

* billing​Agreement​Id

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The billing agreement ID from PayPal that starts with 'B-' (for example, `B-1234XXXXX`).

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer.

* inactive

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether the PayPal billing agreement is inactive.

***

## Customer​Payment​Method​Paypal​Billing​Agreement​Create​Payload returns

* customer​Payment​Method

  [Customer​Payment​Method](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethod)

  The customer payment method.

* user​Errors

  [\[Customer​Payment​Method​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethodUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerPaymentMethodPaypalBillingAgreementCreate reference
