---
title: dataSaleOptOut - GraphQL Admin
description: Opt out a customer from data sale.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/dataSaleOptOut'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/dataSaleOptOut.md
---

# data​Sale​Opt​Out

mutation

Requires `write_privacy_settings` access scope.

Opt out a customer from data sale.

## Arguments

* email

  [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  required

  The email address of the customer to opt out of data sale.

***

## Data​Sale​Opt​Out​Payload returns

* customer​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the customer whose email address has been opted out of data sale.

* user​Errors

  [\[Data​Sale​Opt​Out​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DataSaleOptOutUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### dataSaleOptOut reference
