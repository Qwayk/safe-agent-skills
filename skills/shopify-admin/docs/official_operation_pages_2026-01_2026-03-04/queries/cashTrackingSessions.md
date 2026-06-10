---
title: cashTrackingSessions - GraphQL Admin
description: >-
  Returns a shop's cash tracking sessions for locations with a POS Pro
  subscription.


  Tip: To query for cash tracking sessions in bulk, you can

  [perform a bulk
  operation](https://shopify.dev/docs/api/usage/bulk-operations/queries).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/cashTrackingSessions
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/cashTrackingSessions.md
---

# cash​Tracking​Sessions

query

Returns a shop's cash tracking sessions for locations with a POS Pro subscription.

Tip: To query for cash tracking sessions in bulk, you can [perform a bulk operation](https://shopify.dev/docs/api/usage/bulk-operations/queries).

## CashTrackingSessionConnection arguments

[CashTrackingSessionConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/CashTrackingSessionConnection)

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

  A filter made up of terms, connectives, modifiers, and comparators. You can apply one or more filters to a query. Learn more about [Shopify API search syntax](https://shopify.dev/api/usage/search-syntax).

  * closing\_time

    time

  * * id

      id

    * location\_id

      id

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * opening\_time

    time

  * point\_of\_sale\_device\_ids

    string

  * status

    string

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Cash​Tracking​Sessions​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/CashTrackingSessionsSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Cash​Tracking​Session​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CashTrackingSessionEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Cash​Tracking​Session!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/CashTrackingSession)

  non-null

  A list of nodes that are contained in CashTrackingSessionEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### cashTrackingSessions reference
