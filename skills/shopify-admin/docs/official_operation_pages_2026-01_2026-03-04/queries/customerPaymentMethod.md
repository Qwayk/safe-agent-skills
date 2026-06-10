---
title: customerPaymentMethod - GraphQL Admin
description: Returns a CustomerPaymentMethod resource by its ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerPaymentMethod
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/customerPaymentMethod.md
---

# customer​Payment​Method

query

Returns a CustomerPaymentMethod resource by its ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the CustomerPaymentMethod to return.

* show​Revoked

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Whether to show the customer's revoked payment method.

***

## Possible returns

* Customer​Payment​Method

  [Customer​Payment​Method](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerPaymentMethod)

  A customer's saved payment method. Stores the payment instrument details and billing information for recurring charges.

  The payment method supports types included in the [`CustomerPaymentInstrument`](https://shopify.dev/docs/api/admin-graphql/latest/unions/CustomerPaymentInstrument) union.

  * customer

    [Customer](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)

    The customer to whom the payment method belongs.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The ID of this payment method.

  * instrument

    [Customer​Payment​Instrument](https://shopify.dev/docs/api/admin-graphql/latest/unions/CustomerPaymentInstrument)

    The instrument for this payment method.

  * mandates

    [Payment​Mandate​Resource​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/PaymentMandateResourceConnection)

    non-null

    The mandates associated with the payment method.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

  * revoked​At

    [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

    The time that the payment method was revoked.

  * revoked​Reason

    [Customer​Payment​Method​Revocation​Reason](https://shopify.dev/docs/api/admin-graphql/latest/enums/CustomerPaymentMethodRevocationReason)

    The revocation reason for this payment method.

  * subscription​Contracts

    [Subscription​Contract​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionContractConnection)

    non-null

    List Subscription Contracts.

    * first

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      ### Arguments

      The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * after

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * last

      [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

      The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

    * before

      [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

      The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

    * reverse

      [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

      Default:false

      Reverse the order of the underlying list.

    ***

***

## Examples

* ### customerPaymentMethod reference
