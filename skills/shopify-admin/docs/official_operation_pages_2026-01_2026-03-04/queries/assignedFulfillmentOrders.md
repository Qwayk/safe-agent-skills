---
title: assignedFulfillmentOrders - GraphQL Admin
description: >-
  The paginated list of fulfillment orders assigned to the shop locations owned
  by the app.


  Assigned fulfillment orders are fulfillment orders that are set to be
  fulfilled from locations

  managed by

  [fulfillment
  services](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentService)

  that are registered by the app.

  One app (api_client) can host multiple fulfillment services on a shop.

  Each fulfillment service manages a dedicated location on a shop.

  Assigned fulfillment orders can have associated

  [fulfillment
  requests](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderRequestStatus),

  or might currently not be requested to be fulfilled.


  The app must have the `read_assigned_fulfillment_orders`

  [access scope](https://shopify.dev/docs/api/usage/access-scopes)

  to be able to retrieve the fulfillment orders assigned to its locations.


  All assigned fulfillment orders (except those with the `CLOSED` status) will
  be returned by default.

  Perform filtering with the `assignmentStatus` argument

  to receive only fulfillment orders that have been requested to be fulfilled.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/assignedFulfillmentOrders
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/assignedFulfillmentOrders.md
---

# assigned​Fulfillment​Orders

query

Requires `read_assigned_fulfillment_orders` access scope.

The paginated list of fulfillment orders assigned to the shop locations owned by the app.

Assigned fulfillment orders are fulfillment orders that are set to be fulfilled from locations managed by [fulfillment services](https://shopify.dev/api/admin-graphql/latest/objects/FulfillmentService) that are registered by the app. One app (api\_client) can host multiple fulfillment services on a shop. Each fulfillment service manages a dedicated location on a shop. Assigned fulfillment orders can have associated [fulfillment requests](https://shopify.dev/api/admin-graphql/latest/enums/FulfillmentOrderRequestStatus), or might currently not be requested to be fulfilled.

The app must have the `read_assigned_fulfillment_orders` [access scope](https://shopify.dev/docs/api/usage/access-scopes) to be able to retrieve the fulfillment orders assigned to its locations.

All assigned fulfillment orders (except those with the `CLOSED` status) will be returned by default. Perform filtering with the `assignmentStatus` argument to receive only fulfillment orders that have been requested to be fulfilled.

## FulfillmentOrderConnection arguments

[FulfillmentOrderConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/FulfillmentOrderConnection)

* after

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come after the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* assignment​Status

  [Fulfillment​Order​Assignment​Status](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderAssignmentStatus)

  The assigment status of the fulfillment orders that should be returned. If `assignmentStatus` argument is not provided, then the query will return all assigned fulfillment orders, except those that have the `CLOSED` status.

* before

  [String](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  The elements that come before the specified [cursor](https://shopify.dev/api/usage/pagination-graphql).

* first

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The first `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* last

  [Int](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Int)

  The last `n` elements from the [paginated list](https://shopify.dev/api/usage/pagination-graphql).

* location​Ids

  [\[ID!\]](https://shopify.dev/docs/api/admin-graphql/latest/scalars/ID)

  Returns fulfillment orders only for certain locations, specified by a list of location IDs.

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Fulfillment​Order​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/FulfillmentOrderSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

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

* ### assignedFulfillmentOrders reference
