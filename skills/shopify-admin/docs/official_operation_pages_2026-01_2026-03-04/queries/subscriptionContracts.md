---
title: subscriptionContracts - GraphQL Admin
description: >-
  Returns a
  [`SubscriptionContractConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContractConnection)
  containing [subscription
  contracts](https://shopify.dev/docs/api/customer/latest/objects/SubscriptionContract).
  Subscription contracts are agreements between
  [customers](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer)
  and merchants for recurring purchases with defined billing and delivery
  schedules.


  Filter results with the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionContracts#arguments-query)
  argument. You can paginate results using standard [cursor-based
  pagination](https://shopify.dev/docs/api/usage/pagination-graphql).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionContracts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionContracts.md
---

# subscription​Contracts

query

Returns a [`SubscriptionContractConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContractConnection) containing [subscription contracts](https://shopify.dev/docs/api/customer/latest/objects/SubscriptionContract). Subscription contracts are agreements between [customers](https://shopify.dev/docs/api/admin-graphql/latest/objects/Customer) and merchants for recurring purchases with defined billing and delivery schedules.

Filter results with the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionContracts#arguments-query) argument. You can paginate results using standard [cursor-based pagination](https://shopify.dev/docs/api/usage/pagination-graphql).

## SubscriptionContractConnection arguments

[SubscriptionContractConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionContractConnection)

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

  * created\_at

    time

  * * id

      id

    * last\_billing\_attempt\_error\_type

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * status

    string

  * updated\_at

    time

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Subscription​Contracts​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionContractsSortKeys)

  Default:CREATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Subscription​Contract​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContractEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Subscription​Contract!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionContract)

  non-null

  A list of nodes that are contained in SubscriptionContractEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### subscriptionContracts reference
