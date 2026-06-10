---
title: sellingPlanGroups - GraphQL Admin
description: >-
  Retrieves a paginated list of
  [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)
  objects that belong to the app making the API call. Selling plan groups are
  selling methods like subscriptions, preorders, or other purchase options that
  merchants offer to customers.


  Each group has one or more
  [`SellingPlan`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlan)
  objects that define specific billing and delivery schedules, pricing
  adjustments, and policies. Use the
  [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroups#arguments-query)
  argument to search by name or filter results by other criteria.


  Learn more about [building selling
  plans](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans).
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroups'
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroups.md
---

# selling​Plan​Groups

query

Retrieves a paginated list of [`SellingPlanGroup`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup) objects that belong to the app making the API call. Selling plan groups are selling methods like subscriptions, preorders, or other purchase options that merchants offer to customers.

Each group has one or more [`SellingPlan`](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlan) objects that define specific billing and delivery schedules, pricing adjustments, and policies. Use the [`query`](https://shopify.dev/docs/api/admin-graphql/latest/queries/sellingPlanGroups#arguments-query) argument to search by name or filter results by other criteria.

Learn more about [building selling plans](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans).

## SellingPlanGroupConnection arguments

[SellingPlanGroupConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SellingPlanGroupConnection)

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

  * * default

      string

    * app\_id

      id

    * category

      string

    * created\_at

      time

    - Filter by a case-insensitive search of multiple fields in a document.

    - Example:
      * `query=Bob Norman`
      * `query=title:green hoodie`

    - Valid values:

      * `CURRENT` Default
      * `ALL`
      * `* (numeric app ID)`

      A comma-separated list of categories.

    - Valid values:
      * `SUBSCRIPTION`
      * `PRE_ORDER`
      * `TRY_BEFORE_YOU_BUY`
      * `OTHER`

  * delivery\_frequency

    string

  * * id

      id

    * name

      string

    - Filter by `id` range.

    - Example:
      * `id:1234`
      * `id:>=1234`
      * `id:<=1234`

  * percentage\_off

    float

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

* sort​Key

  [Selling​Plan​Group​Sort​Keys](https://shopify.dev/docs/api/admin-graphql/latest/enums/SellingPlanGroupSortKeys)

  Default:ID

  Sort the underlying list using a key. If your query is slow or returns an error, then [try specifying a sort key that matches the field used in the search](https://shopify.dev/api/usage/pagination-graphql#search-performance-considerations).

***

## Possible returns

* edges

  [\[Selling​Plan​Group​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroupEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Selling​Plan​Group!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SellingPlanGroup)

  non-null

  A list of nodes that are contained in SellingPlanGroupEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### sellingPlanGroups reference
