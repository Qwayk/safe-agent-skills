---
title: reverseDelivery - GraphQL Admin
description: Lookup a reverse delivery by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/reverseDelivery'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/reverseDelivery.md'
---

# reverse​Delivery

query

Requires `read_returns` access scope or `read_marketplace_returns` access scope.

Lookup a reverse delivery by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the ReverseDelivery to return.

***

## Possible returns

* Reverse​Delivery

  [Reverse​Delivery](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseDelivery)

  A reverse delivery is a post-fulfillment object that represents a buyer sending a package to a merchant. For example, a buyer requests a return, and a merchant sends the buyer a shipping label. The reverse delivery contains the context of the items sent back, how they're being sent back (for example, a shipping label), and the current state of the delivery (tracking information).

  * deliverable

    [Reverse​Delivery​Deliverable](https://shopify.dev/docs/api/admin-graphql/latest/unions/ReverseDeliveryDeliverable)

    The deliverable associated with the reverse delivery.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    The ID of the reverse delivery.

  * reverse​Delivery​Line​Items

    [Reverse​Delivery​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReverseDeliveryLineItemConnection)

    non-null

    The reverse delivery line items attached to the reverse delivery.

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

  * reverse​Fulfillment​Order

    [Reverse​Fulfillment​Order!](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseFulfillmentOrder)

    non-null

    The `ReverseFulfillmentOrder` associated with the reverse delivery.

***

## Examples

* ### reverseDelivery reference
