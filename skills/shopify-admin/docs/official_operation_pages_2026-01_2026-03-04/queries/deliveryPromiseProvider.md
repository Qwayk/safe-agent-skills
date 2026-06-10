---
title: deliveryPromiseProvider - GraphQL Admin
description: Lookup a delivery promise provider.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseProvider
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/deliveryPromiseProvider.md
---

# delivery​Promise​Provider

query

Requires `read_delivery_promises` access scope.

Lookup a delivery promise provider.

## Arguments

* location​Id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the location associated with the delivery promise provider.

***

## Possible returns

* Delivery​Promise​Provider

  [Delivery​Promise​Provider](https://shopify.dev/docs/api/admin-graphql/latest/objects/DeliveryPromiseProvider)

  A delivery promise provider. Currently restricted to select approved delivery promise partners.

  * active

    [Boolean!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

    non-null

    Whether the delivery promise provider is active. Defaults to `true` when creating a provider.

  * fulfillment​Delay

    [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

    The number of seconds to add to the current time as a buffer when looking up delivery promises. Represents how long the shop requires before releasing an order to the fulfillment provider.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * location

    [Location!](https://shopify.dev/docs/api/admin-graphql/latest/objects/Location)

    non-null

    The location associated with this delivery promise provider.

  * time​Zone

    [String!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

    non-null

    The time zone to be used for interpreting day of week and cutoff times in delivery schedules when looking up delivery promises.

***

## Examples

* ### deliveryPromiseProvider reference
