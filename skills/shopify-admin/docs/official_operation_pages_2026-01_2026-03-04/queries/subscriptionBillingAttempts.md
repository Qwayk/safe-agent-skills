---
title: subscriptionBillingAttempts - GraphQL Admin
description: Returns subscription billing attempts on a store.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingAttempts
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionBillingAttempts.md
---

# subscription​Billing​Attempts

query

Returns subscription billing attempts on a store.

## SubscriptionBillingAttemptConnection arguments

[SubscriptionBillingAttemptConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SubscriptionBillingAttemptConnection)

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

  * error\_code

    string

  * error\_message

    string

  * id

    id

    Filter by `id` range.

    Example:

    * `id:1234`
    * `id:>=1234`
    * `id:<=1234`

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Subscription​Billing​Attempts​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/SubscriptionBillingAttemptsSortKeys)

  Default:CREATED\_AT

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Subscription​Billing​Attempt​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingAttemptEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Subscription​Billing​Attempt!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SubscriptionBillingAttempt)

  non-null

  A list of nodes that are contained in SubscriptionBillingAttemptEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### subscriptionBillingAttempts reference
