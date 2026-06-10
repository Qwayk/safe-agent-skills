---
title: taxSummaryCreate - GraphQL Admin
description: >-
  Creates a tax summary for a given order.

  If both an order ID and a start and end time are provided, the order ID will
  be used.
api_version: 2026-01
api_name: admin
type: mutation
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/mutations/taxSummaryCreate'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/mutations/taxSummaryCreate.md
---

# tax​Summary​Create

mutation

Requires `write_taxes` access scope. Also: The caller must be a tax calculations app and the relevant feature must be on.

Creates a tax summary for a given order. If both an order ID and a start and end time are provided, the order ID will be used.

## Arguments

* end​Time

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The end time of the range of orders to create the tax summary for.

* order​Id

  [ID](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  The ID of the order to create the tax summary for.

* start​Time

  [Date​Time](https://shopify.dev/docs/api/admin-graphql/latest/scalars/DateTime)

  The start time of the range of orders to create the tax summary for.

***

## Tax​Summary​Create​Payload returns

* enqueued​Orders

  [\[Order!\]](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

  A list of orders that were successfully enqueued to create a tax summary.

* user​Errors

  [\[Tax​Summary​Create​User​Error!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/TaxSummaryCreateUserError)

  non-null

  The list of errors that occurred from executing the mutation.

***

## Examples

* ### taxSummaryCreate reference
