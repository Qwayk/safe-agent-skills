---
title: customerCancelDataErasure - GraphQL Admin
description: >-
  Cancels a pending erasure of a customer's data. Read more
  [here](https://help.shopify.com/manual/privacy-and-security/privacy/processing-customer-data-requests#cancel-customer-data-erasure).


  To request an erasure of a customer's data use the [customerRequestDataErasure
  mutation](https://shopify.dev/api/admin-graphql/unstable/mutations/customerRequestDataErasure).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerCancelDataErasure
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerCancelDataErasure.md
---

# customer​Cancel​Data​Erasure

mutation

Requires `write_customer_data_erasure` access scope. Also: The user must have access to erase customer data.

Cancels a pending erasure of a customer's data. Read more [here](https://help.shopify.com/manual/privacy-and-security/privacy/processing-customer-data-requests#cancel-customer-data-erasure).

To request an erasure of a customer's data use the [customerRequestDataErasure mutation](https://shopify.dev/api/admin-graphql/unstable/mutations/customerRequestDataErasure).

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer for whom to cancel a pending data erasure.

***

## Customer​Cancel​Data​Erasure​Payload returns

* customer​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the customer whose pending data erasure has been cancelled.

* user​Errors

  [\[Customer​Cancel​Data​Erasure​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerCancelDataErasureUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerCancelDataErasure reference
