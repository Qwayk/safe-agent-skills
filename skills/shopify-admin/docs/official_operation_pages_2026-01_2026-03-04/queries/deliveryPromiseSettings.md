---
title: deliveryPromiseSettings - GraphQL Admin
description: Represents the delivery promise settings for a shop.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseSettings
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseSettings.md
---

# delivery​Promise​Settings

query

Requires `read_shipping` access scope or `read_shop_promise_program` access scope.

Represents the delivery promise settings for a shop.

## Possible returns

* Delivery​Promise​Setting

  [Delivery​Promise​Setting!](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryPromiseSetting)

  The delivery promise settings.

  * delivery​Dates​Enabled

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether delivery dates is enabled.

  * processing​Time

    [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    The number of business days required for processing the order before the package is handed off to the carrier. Expressed as an ISO8601 duration.

***

## Examples

* ### deliveryPromiseSettings reference
