---
title: codeDiscountSavedSearches - GraphQL Admin
description: List of the shop's code discount saved searches.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountSavedSearches
  md: >-
    https://shopify.dev/docs/api/admin-graphql/latest/queries/codeDiscountSavedSearches.md
---

# code​Discount​Saved​Searches

query

List of the shop's code discount saved searches.

## SavedSearchConnection arguments

[SavedSearchConnection!](https://shopify.dev/docs/api/admin-graphql/latest/connections/SavedSearchConnection)

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

* reverse

  [Boolean](https://shopify.dev/docs/api/admin-graphql/latest/scalars/Boolean)

  Default:false

  Reverse the order of the underlying list.

***

## Possible returns

* edges

  [\[Saved​Search​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearchEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[Saved​Search!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/SavedSearch)

  non-null

  A list of nodes that are contained in SavedSearchEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### codeDiscountSavedSearches reference
