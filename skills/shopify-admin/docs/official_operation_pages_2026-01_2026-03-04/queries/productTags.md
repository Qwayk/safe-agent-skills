---
title: productTags - GraphQL Admin
description: >-
  Returns tags added to
  [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product)
  objects in the shop. Provides a paginated list of tag strings.


  The maximum page size is 5000 tags per request. Tags are returned as simple
  strings through a
  [`StringConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StringConnection).

  The maximum page size is 5000.
api_version: 2026-01
api_name: admin
type: query
api_type: graphql
source_url:
  html: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/productTags'
  md: 'https://shopify.dev/docs/api/admin-graphql/latest/queries/productTags.md'
---

# product​Tags

query

Requires Requires `read_products` access scope.

Returns tags added to [`Product`](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product) objects in the shop. Provides a paginated list of tag strings.

The maximum page size is 5000 tags per request. Tags are returned as simple strings through a [`StringConnection`](https://shopify.dev/docs/api/admin-graphql/latest/objects/StringConnection). The maximum page size is 5000.

## StringConnection arguments

[StringConnection](https://shopify.dev/docs/api/admin-graphql/latest/connections/StringConnection)

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

  [\[String​Edge!\]!](https://shopify.dev/docs/api/admin-graphql/latest/objects/StringEdge)

  non-null

  The connection between the node and its parent. Each edge contains a minimum of the edge's cursor and the node.

* nodes

  [\[String!\]!](https://shopify.dev/docs/api/admin-graphql/latest/scalars/String)

  non-null

  A list of nodes that are contained in StringEdge. You can fetch data about an individual node, or you can follow the edges to fetch data about a collection of related nodes. At each node, you specify the fields that you want to retrieve.

* page​Info

  [Page​Info!](https://shopify.dev/docs/api/admin-graphql/latest/objects/PageInfo)

  non-null

  An object that’s used to retrieve [cursor information](https://shopify.dev/api/usage/pagination-graphql) about the current page.

***

## Examples

* ### productTags reference
