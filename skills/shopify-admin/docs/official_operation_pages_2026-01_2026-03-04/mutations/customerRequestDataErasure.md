---
title: customerRequestDataErasure - GraphQL Admin
description: >-
  Enqueues a request to erase customer's data. Read more
  [here](https://help.shopify.com/manual/privacy-and-security/privacy/processing-customer-data-requests#erase-customer-personal-data).


  To cancel the data erasure request use the [customerCancelDataErasure
  mutation](https://shopify.dev/api/admin-graphql/unstable/mutations/customerCancelDataErasure).
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerRequestDataErasure
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/customerRequestDataErasure.md
---

# customer​Request​Data​Erasure

mutation

Requires `write_customer_data_erasure` access scope. Also: The user must have access to erase customer data.

Enqueues a request to erase customer's data. Read more [here](https://help.shopify.com/manual/privacy-and-security/privacy/processing-customer-data-requests#erase-customer-personal-data).

To cancel the data erasure request use the [customerCancelDataErasure mutation](https://shopify.dev/api/admin-graphql/unstable/mutations/customerCancelDataErasure).

## Arguments

* customer​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the customer to erase.

***

## Customer​Request​Data​Erasure​Payload returns

* customer​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the customer that will be erased.

* user​Errors

  [\[Customer​Request​Data​Erasure​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CustomerRequestDataErasureUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### customerRequestDataErasure reference
