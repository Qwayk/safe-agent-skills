---
title: reverseFulfillmentOrder - GraphQL Admin
description: Lookup a reverse fulfillment order by ID.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/reverseFulfillmentOrder
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/reverseFulfillmentOrder.md
---

# reverse​Fulfillment​Order

query

Requires `read_returns` access scope or `read_marketplace_returns` access scope.

Lookup a reverse fulfillment order by ID.

## Arguments

* id

  [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  required

  The ID of the reverse fulfillment order to return.

***

## Possible returns

* Reverse​Fulfillment​Order

  [Reverse​Fulfillment​Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseFulfillmentOrder)

  A group of one or more items in a return that will be processed at a fulfillment service. There can be more than one reverse fulfillment order for a return at a given location.

  * id

    [ID!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

    non-null

    A globally-unique ID.

  * line​Items

    [Reverse​Fulfillment​Order​Line​Item​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReverseFulfillmentOrderLineItemConnection)

    non-null

    The list of reverse fulfillment order line items for the reverse fulfillment order.

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

  * order

    [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order)

    The order associated with the reverse fulfillment order.

  * reverse​Deliveries

    [Reverse​Delivery​Connection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/ReverseDeliveryConnection)

    non-null

    The list of reverse deliveries for the reverse fulfillment order.

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

  * status

    [Reverse​Fulfillment​Order​Status!](https://shopify.dev/docs/api/admin-graphql/latest/enums/ReverseFulfillmentOrderStatus)

    non-null

    The status of the reverse fulfillment order.

  * third​Party​Confirmation

    [Reverse​Fulfillment​Order​Third​Party​Confirmation](https://shopify.dev/docs/api/admin-graphql/latest/objects/ReverseFulfillmentOrderThirdPartyConfirmation)

    The current confirmation for the reverse fulfillment order from a third-party logistics service. If no third-party service is involved, then this value is `nil`.

***

## Examples

* ### reverseFulfillmentOrder reference
