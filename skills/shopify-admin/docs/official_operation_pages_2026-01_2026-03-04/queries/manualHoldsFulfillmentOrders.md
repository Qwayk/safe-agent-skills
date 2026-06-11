---
title: manualHoldsFulfillmentOrders - GraphQL Admin
description: Returns a list of fulfillment orders that are on hold.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/manualHoldsFulfillmentOrders
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/manualHoldsFulfillmentOrders.md
---

# manual​Holds​Fulfillment​Orders

query

Requires `read_orders` access scope.

Returns a list of fulfillment orders that are on hold.

## FulfillmentOrderConnection arguments

[FulfillmentOrderConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* query

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The query conditions used to filter fulfillment orders. Only fulfillment orders corresponding to orders matching the query will be counted. Supported filter parameters:

  * `order_financial_status`
  * `order_risk_level`
  * `shipping_address_coordinates_validated`

  See the detailed [search syntax](https://shopify.dev/api/usage/search-syntax) for more information about using filters.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Fulfillment​Order​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrderEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Fulfillment​Order!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/FulfillmentOrder)

  non-null

  A list of nodes that are contained in FulfillmentOrderEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### manualHoldsFulfillmentOrders reference
